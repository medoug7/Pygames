
# @author medoug7

import pygame as pg
import pymunk as pm
import numpy as np
import random

# define o espaço que pode interagir
space = pm.Space()
#space.gravity = (0, -500) # gravidade

pg.init()
# informação da janela
win_len, win_hei = 1000, 500
win = pg.display.set_mode((win_len,win_hei))
pg.display.set_caption('Pong')
#draw_options = pm.pygame_util.DrawOptions(win)

# relógio
clock = pg.time.Clock()
FPS = 60

left = 25
right = win_len-left
bottom = 35
top = win_hei-bottom
midy = win_hei/2
midx = win_len/2


pg.font.init()
FONT = pg.font.SysFont('comicsans', 30)


# colocar a origem onde ela devia estar (canto inferior esquerdo)
def conv_coords(point):
	# pymunk permite posições em float, e o pygame usa int
	# é preciso concerter entre os dois
	return (int(point[0]), int(win_hei-point[1]))


class Ball():
	def __init__(self):
		self.radius = 8
		self.body = pm.Body()
		self.reset(0,0,0)

		self.shape = pm.Circle(self.body, self.radius, (0, 0))
		self.shape.elasticity = 1
		self.shape.density = 1
		#shape.friction = 0.9
		space.add(self.body, self.shape)
		self.shape.collision_type = 1

	def draw(self, win):
		pg.draw.circle(win, (255,255,255), conv_coords(self.body.position), self.radius)

	# como o pymunk lida com colisões (vai reiniciar a bola)
	def reset(self, space, arbiter, data):
		self.body.position = (midx, midy)
		self.body.velocity = (400*random.choice([-1,1]),300*random.choice([-1,1]))
		return False

	# velocidade padrão das colisões
	def vel_col(self, space, arbiter, data):
		self.body.velocity = self.body.velocity*(700/self.body.velocity.length)


class Walls():
	def __init__(self, a, b, collision_n=None):
		# pontos inicial e final da linha
		self.a, self.b = a, b
		self.body = pm.Body(body_type=pm.Body.STATIC)
		self.shape = pm.Segment(self.body, a, b, 5)
		self.shape.elasticity = 1
		space.add(self.body, self.shape)

		if collision_n:
			self.shape.collision_type = collision_n

	def draw(self, win):
		pg.draw.line(win, (255,255,255), self.a, self.b, 5)


class Player():
	def __init__(self, x):
		self.body = pm.Body(body_type=pm.Body.KINEMATIC)
		self.body.position = (x, midy)
		# posição relativa (body, offset_a, offset_b)
		self.size = 40
		self.shape = pm.Segment(self.body, (0,-self.size), (0,self.size), 5)
		self.shape.elasticity = 1
		space.add(self.body, self.shape)
		
		self.shape.collision_type = 4
		self.score = 0

	def draw(self, win):
		# temos que sair da posição relativa pra posição global
		p1 = self.body.local_to_world(self.shape.a)
		p2 = self.body.local_to_world(self.shape.b)
		pg.draw.line(win, (255,255,255), conv_coords(p1), conv_coords(p2), 5)

	def move(self, up=True):
		if up:
			self.body.velocity = (0, 600)
		else:
			self.body.velocity = (0, -600)

	def stop(self):
		self.body.velocity = (0, 0)

	def borda(self):
		if self.body.local_to_world(self.shape.a)[1] + 2*self.size >= top:
			self.body.velocity = (0,0)
			self.body.position = (self.body.position[0],top-self.size)
		if self.body.local_to_world(self.shape.b)[1] -2*self.size <= bottom:
			self.body.velocity = (0,0)
			self.body.position = (self.body.position[0],bottom+self.size)


# desenhar o mundo
def redraw(win, ball, walls, ps):
	win.fill((0,0,0)) # fundo preto

	# desenha a bola
	ball.draw(win)
	# desenha as paredes
	[wall.draw(win) for wall in walls]
	# desenha os jogadores
	[player.draw(win) for player in ps]

	pg.draw.line(win, (255,255,255), (midx, top), (midx, bottom), 5)

	# pontuação
	text = FONT.render(str(int(ps[0].score)), 0, (255,255,255)) # pontuação
	win.blit(text, (midx+10, 10))
	text = FONT.render(str(int(ps[1].score)), 0, (255,255,255)) # pontuação
	win.blit(text, (midx-10-text.get_width(), 10))


	pg.display.update()



def main():
	run = True

	# chão e teto
	floor = Walls((left, bottom), (right, bottom))
	ceil = Walls((left, top), (right, top))
	# as laterais tem collis_n=2 pra identificarmos quando
	# a bola (coll_n=1) bate nelas
	w_left = Walls((left, top), (left, bottom), 2)
	w_right = Walls((right, top), (right, bottom), 3)
	walls = [floor, ceil, w_left, w_right]

	# coloca uma bola (massa, pos)
	ball = Ball()
	
	# jogadores
	p1 = Player(right-20)
	p2 = Player(left+20)
	Ps = [p1, p2]

	# como detectar colisões (os pontos)
	scored_1 = space.add_collision_handler(1,2)
	scored_2 = space.add_collision_handler(1,3)
	def ponto_p1(space, arbiter, data):
		p1.score += 1
		ball.reset(0,0,0)
		return False
	def ponto_p2(space, arbiter, data):
		p2.score += 1
		ball.reset(0,0,0)
		return False

	# begin: quando dois objetos se tocam
	scored_1.begin = ponto_p1
	scored_2.begin = ponto_p2

	# velocidade padrão ao bater na bola
	contact = space.add_collision_handler(1,4)
	# post_solve: depois da colisão
	contact.post_solve = ball.vel_col

	# Main loop
	while run:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False

		keys = pg.key.get_pressed()
		
		# P1 usa setinhas
		if not p1.borda():
			if keys[pg.K_UP]:
				p1.move()
			elif keys[pg.K_DOWN]:
				p1.move(up=False)
			else:
				p1.stop()

		# P2 usa W e S
		if not p2.borda():
			if keys[pg.K_w]:
				p2.move()
			elif keys[pg.K_s]:
				p2.move(up=False)
			else:
				p2.stop()


		# calcula toda a física
		space.step(1/FPS)

		redraw(win, ball, walls, Ps)
		# Delay fixed time between frames
		clock.tick(FPS)


main()
pg.quit()


