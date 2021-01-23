

import pygame as pg
import random


DINO_RUN = [pg.transform.scale2x(pg.image.load('dino/dino3.png')), pg.transform.scale2x(pg.image.load('dino/dino4.png'))]
DINO_LOW = [pg.transform.scale2x(pg.image.load('dino/dino_l1.png')), pg.transform.scale2x(pg.image.load('dino/dino_l2.png'))]
DINO_JUMP = pg.transform.scale2x(pg.image.load('dino/dino2.png'))
DINO_DEAD = pg.transform.scale2x(pg.image.load('dino/dinod.png'))
BIRD = [pg.transform.scale2x(pg.image.load('dino/bird1.png')), pg.transform.scale2x(pg.image.load('dino/bird2.png'))]
CACTI = [pg.transform.scale2x(pg.image.load('dino/cac1.png')), pg.transform.scale2x(pg.image.load('dino/cac2.png')), pg.transform.scale2x(pg.image.load('dino/cac3.png')), pg.transform.scale2x(pg.image.load('dino/cac4.png')), pg.transform.scale2x(pg.image.load('dino/cac5.png')),pg.transform.scale2x(pg.image.load('dino/m_cac1.png')), pg.transform.scale2x(pg.image.load('dino/m_cac2.png')), pg.transform.scale2x(pg.image.load('dino/M_cac3.png')), pg.transform.scale2x(pg.image.load('dino/m_cac4.png'))]
BASE = pg.transform.scale2x(pg.image.load('dino/base.png'))
CLOUD = pg.transform.scale2x(pg.image.load('dino/cloud.png'))
DIRT = [pg.transform.scale2x(pg.image.load('dino/dirt1.png')), pg.transform.scale2x(pg.image.load('dino/dirt2.png'))]
OVER = pg.transform.scale2x(pg.image.load('dino/over.png'))

WIN_WID = 700
WIN_HEI = 300

floor = 250 # posição do chão

class Dino():
	MAX_ROT = 25
	ANIM_TIME = 2.5
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tick_ct = 0
		self.vel = -10
		self.height = self.y
		self.img_ct = 0
		self.img = DINO_RUN[0]
		self.isJump = False
		self.jumpct = 0 # cooldown do pulo
		self.isLow = False
		self.isDead = False
		

	def jump(self):
		self.tick_ct = 0
		self.isJump = True
		self.height = self.y

	def move(self):
		self.tick_ct += 1
		if self.tick_ct < 10:
			d = self.vel*self.tick_ct + (self.tick_ct)**2
		elif self.tick_ct <= 12:
			d = 0
		elif self.tick_ct > 12:
			d = (self.tick_ct - 12)**2

		if self.isJump:
			self.y = self.y + d
		if self.y > floor - 40:
			self.y = floor - 40

		if self.jumpct == 0:
			self.isJump = False
		elif self.jumpct > 0:
			self.jumpct -= 1


	# desenha o dino correndo, pulando e se abaixando
	def draw(self, win):
		self.img_ct += 1

		if self.isJump:
			self.img = DINO_JUMP
			self.img_ct = 0
		elif self.img_ct < self.ANIM_TIME:
			self.img = DINO_RUN[0]
		elif self.img_ct < self.ANIM_TIME*2:
			self.img = DINO_RUN[1]
		elif self.img_ct < 2*self.ANIM_TIME+1:
			self.img_ct = 0

		if self.isLow:
			if self.img_ct < self.ANIM_TIME:
				self.img = DINO_LOW[0]
			elif self.img_ct < self.ANIM_TIME*2:
				self.img = DINO_LOW[1]
			elif self.img_ct < 2*self.ANIM_TIME+1:
				self.img_ct = 0

		win.blit(self.img, (self.x,self.y))


	# morre (só será usado se o jogador for humano)
	def die(self,win):
		self.x = 80
		self.y = floor - 40
		self.tick_ct = 0
		self.height = self.y
		self.img_ct = 0
		self.isJump = False
		self.isLow = False

		win.blit(OVER, (WIN_WID/2 - OVER.get_width()/2, WIN_HEI/2))

		pg.display.update()
		self.img = DINO_RUN[0]
		i = 0
		while i < 200:
			pg.time.delay(10)
			i += 1
			for event in pg.event.get():
				if event.type == pg.QUIT:
					i = 201
					run = False

		self.isDead = False


	# máscara para colisões mais precisas        
	def get_mask(self):
		return pg.mask.from_surface(self.img)


class Cactus():
	
	def __init__(self, x):
		self.x = x
		self.img_ct = random.randrange(0, 9)
		self.img = CACTI[int(self.img_ct)]
		self.passed = False
		self.height = floor+15-self.img.get_height()
		self.width = self.img.get_width()
	
	# mover
	def move(self, floor_v):
		self.x -= floor_v
		
	# desenha
	def draw(self, win):
		win.blit(self.img, (self.x, self.height))

	# colisões
	def collide(self, dino):
		dino_mask = dino.get_mask()
		cac_mask = pg.mask.from_surface(self.img)

		offset = (self.x - dino.x, self.height - round(dino.y))

		t_point = dino_mask.overlap(cac_mask, offset)

		if t_point:
			return True
		else:
			return False

class Bird():
	ANIM_TIME = 5
	
	def __init__(self, x):
		self.x = x
		height = random.randint(0,3)
		if height == 0:
			self.y = floor-65
		elif height == 1:
			self.y = floor-100
		else:
			self.y = floor-170
			
		
		self.img_ct = 0
		self.img = BIRD[0]
		self.passed = False
	
	# mover
	def move(self, floor_v):
		self.x -= floor_v*2
		
	# desenha
	def draw(self, win):
		self.img_ct += 1

		if self.img_ct < self.ANIM_TIME:
			self.img = BIRD[0]
		elif self.img_ct < self.ANIM_TIME*2:
			self.img = BIRD[1]
		elif self.img_ct < self.ANIM_TIME*2 + 1:
			self.img = BIRD[0]
			self.img_ct = 0

		win.blit(self.img, (self.x, self.y))

	# colisões
	def collide(self, dino):
		dino_mask = dino.get_mask()
		bird_mask = pg.mask.from_surface(self.img)

		offset = (self.x - dino.x, self.y - round(dino.y))

		t_point = dino_mask.overlap(bird_mask, offset)

		if t_point:
			return True
		else:
			return False

class Cloud():
	IMG = CLOUD

	def __init__(self, x):
		height = random.randint(50,200)
		self.y = floor-height
		self.x = x
		self.img = self.IMG

	def move(self, floor_v):
		self.x -= floor_v

	# desenha
	def draw(self, win):
		win.blit(self.img, (self.x, self.y))



class Base():
	WID = BASE.get_width()
	IMG = BASE
	
	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WID
		
	def move(self, floor_v):
		self.x1 -= floor_v
		self.x2 -= floor_v
		
		if self.x1 + self.WID < 0:
			self.x1 = self.x2 + self.WID
		if self.x2 + self.WID < 0:
			self.x2 = self.x1 + self.WID
		
	def draw(self, win):
		win.blit(self.IMG, (self.x1,self.y))
		win.blit(self.IMG, (self.x2,self.y))  
