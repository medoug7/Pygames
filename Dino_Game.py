# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 17:34:34 2020

@author: medou
"""

import pygame as pg
import time
import os
import random

from dino_assets import Dino, Cactus, Bird, Cloud, Base, floor


pg.font.init()
FONT = pg.font.SysFont('comicsans', 30)

WIN_WID = 700
WIN_HEI = 300

TRY = 1
b_score = 0

# desenhar o mundo
def redraw(win, dino, cactus, flock, clouds, base, score, b_score):
	global TRY

	win.fill((255,255,255)) # fundo branco

	base.draw(win)
	for puf in clouds:
		puf.draw(win)
	for cac in cactus:
		cac.draw(win)
	for bird in flock:
		bird.draw(win)

	text = FONT.render('Score: '+ str(int(score)), 0, (100,100,100)) # pontuação
	win.blit(text, (WIN_WID - 10 - text.get_width(), 10))

	text = FONT.render('best: '+ str(int(b_score)), 0, (100,100,100)) # pontuação
	win.blit(text, (WIN_WID - 10 - text.get_width(), 40))

	text = FONT.render('try: ' + str(TRY), 0, (100,100,100))
	win.blit(text, (10, 10))

	
	dino.draw(win)
	pg.display.update()


def main():
	global TRY
	global b_score
	floor_v = 10

	gap_c = 500
	gap_b = 3000

	base = Base(floor)
	dino = Dino(80,floor - 40)
	pos = random.randint(0,gap_c/2)
	cactus = [Cactus(gap_c+pos),Cactus(2*gap_c+pos)]
	flock = [Bird(random.randint(gap_b-500, gap_b+500))]
	clouds =[Cloud(random.randrange(0, WIN_WID)),Cloud(random.randrange(0, WIN_WID))]

	win = pg.display.set_mode((WIN_WID, WIN_HEI))
	pg.display.set_caption('Dino game')
	run = True
	clock = pg.time.Clock()
	score = 0
	p_score = 0
	puf_ct = 0

	while run:
		clock.tick(30)

		# aumenta a dificuldade a cada 50 pontos (velocidade do chão)
		inc_dif = False
		if int(score) % 50 == 0:
			if int(score) > p_score + 10:
				inc_dif = True
			p_score = int(score)
		if inc_dif == True:
			floor_v = floor_v + 1
			inc_dif = False

		# se for sair
		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False

		# comandos
		keys = pg.key.get_pressed()

		# pulo normal
		if keys[pg.K_UP] and dino.jumpct == 0:
			dino.isLow = False
			dino.vel = -8
			dino.jump()
			dino.jumpct = 18

		# pulo alto
		elif keys[pg.K_SPACE] and dino.jumpct == 0:
			dino.isLow = False
			dino.vel = -10
			dino.jump()
			dino.jumpct = 20
			
		# abaixa
		if keys[pg.K_DOWN] and dino.jumpct == 0:
			dino.isLow = True
		else:
			dino.isLow = False


		add_bird = False
		rem_c = [] # lista de cactus para apagar
		rem_b = [] # lista de passaros para apagar
		rem_p = [] #lista de nuvens
		for cac in cactus:
			if cac.collide(dino): # se colide
				dino.isDead = True
				redraw(win, dino, cactus, flock, clouds, base, score, b_score)
				score = 0
				dino.die(win)
				#print('ouch')
				TRY += 1
				add_bird = True
				for cac in cactus:
					rem_c.append(cac)
				for bird in flock:
					rem_b.append(bird)
				floor_v = 10

			if cac.x + cac.img.get_width() < 0:
				rem_c.append(cac)
			
			if not(cac.passed) and cac.x < dino.x:
				cac.passed = True
				add_cac = True
				pass_ct = 1

			cac.move(floor_v)


		for bird in flock:
			if bird.collide(dino): # se colide
				dino.isDead = True
				redraw(win, dino, cactus, flock, clouds, base, score, b_score)
				score = 0
				dino.die(win)
				#print('ouch')
				TRY += 1
				add_bird = True
				for bird in flock:
					rem_b.append(bird)
				for cac in cactus:
					rem_c.append(cac)
				floor_v = 10

			if bird.x + bird.img.get_width() < 0:
				rem_b.append(bird)
			
			if not(bird.passed) and bird.x < dino.x:
				bird.passed = True
				add_bird = True

			bird.move(floor_v)

		puf_ct += 1
		for puf in clouds:
			if puf.x + puf.img.get_width() < 0:
				rem_p.append(puf)

			# move a uma fração da vel do fundo
			if puf_ct == 10:
				puf.move(floor_v)
		if puf_ct == 10:
			puf_ct = 0

		for r in rem_p:
			clouds.remove(r)
		for r in rem_c:
			cactus.remove(r)
		for r in rem_b:
			flock.remove(r)

		if len(clouds) <= 4:
			num = random.randint(2,8)
			gap_c = 300
			while num > 0:
				pos = random.randrange(0,gap_c)
				clouds.append(Cloud(WIN_WID+pos))
				num -= 1
				gap_c = gap_c+pos

		# coloca mais cactus
		if len(cactus) <= 1:
			gap_c = 500*floor_v/10

			if len(cactus) == 0:
				pos = random.randint(0, gap_c)
				cactus.append(Cactus(WIN_WID+pos))

			if len(cactus) == 1:
				num = random.randint(0,5)
				if num < 4:
					pos = random.randint(gap_c, int(3*gap_c/2))
					cactus.append(Cactus(cactus[-1].x+cactus[-1].width+pos))			

				else:
					pos = random.randint(int(gap_c/2), int(2*gap_c/3))
					cactus.append(Cactus(cactus[-1].x+cactus[-1].width+pos))			
				

		# coloca passaros
		if add_bird:
			gap_b = int(3000*floor_v/10)
			pos = random.randrange(gap_b, 3*gap_b)
			flock.append(Bird(gap_b+pos))
			add_bird = False


		if score > b_score:
			b_score = score


		base.move(floor_v)
		dino.move()
		score += 0.1		
		redraw(win, dino, cactus, flock, clouds, base, score, b_score)




main()

pg.quit()
