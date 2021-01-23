
#@author: medoug7

import numpy as np
import pygame as pg
import time
import os
import random
import gzip

try:
	import cPickle as pickle  # pylint: disable=import-error
except ImportError:
	import pickle  # pylint: disable=import-error


from dino_assets import Dino, Cactus, Bird, Cloud, Base, floor

import neat
from neat.population import Population
from neat.reporting import BaseReporter
import visualize


pg.font.init()
FONT = pg.font.SysFont('comicsans', 30)

WIN_WID = 700
WIN_HEI = 300


# desenhar o mundo
def redraw(win, dinos, cactus, flock, clouds, base, score, b_score):
	win.fill((255,255,255)) # fundo branco

	base.draw(win)
	for puf in clouds:
		puf.draw(win)
	for cac in cactus:
		cac.draw(win)
	for bird in flock:
		bird.draw(win)
	
	for dino in dinos:
		dino.draw(win)

	text = FONT.render('score: '+ str(int(score)), 0, (100,100,100)) # pontuação
	win.blit(text, (WIN_WID - 10 - text.get_width(), 10))

	text = FONT.render('best: '+ str(int(b_score)), 0, (100,100,100)) # pontuação
	win.blit(text, (WIN_WID - 10 - text.get_width(), 40))

	text = FONT.render('gen: ' +str(GEN), 0, (100,100,100))
	win.blit(text, (10, 10))

	text = FONT.render('pop: ' +str(len(dinos)), 0, (100,100,100))
	win.blit(text, (10, 40))


	pg.display.update()


# transformar main numa função fitness
def main(genomes, config):
	global GEN
	global b_score
	floor_v = 10

	# define as redes que competem
	nets = []
	ge = []
	dinos = []

	
	# genomas é um tuple (indice, genoma)
	for _,g in genomes:
		
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		dinos.append(Dino(80,floor - 40))
		g.fitness = 0
		ge.append(g)


	base = Base(floor)
	gap_c = 500
	gap_b = 3000

	pos = random.randint(0,gap_c/2)
	cactus = [Cactus(gap_c+pos),Cactus(2*gap_c+pos)]	
	flock = [Bird(random.randint(gap_b-500, gap_b+500))]
	clouds =[Cloud(random.randrange(0, WIN_WID)),Cloud(random.randrange(0, WIN_WID))]

	win = pg.display.set_mode((WIN_WID, WIN_HEI))
	pg.display.set_caption('Dino Evolution')
	run = True
	clock = pg.time.Clock()
	score = 0
	p_score = 0
	puf_ct = 0
	while run:
		clock.tick(30)

		# posicionamento dos cactus
		if len(cactus) <= 2:
			gap_c = 500*floor_v/10

			if len(cactus) == 1:
				pos = random.randint(0, gap_c)
				cactus.append(Cactus(WIN_WID+pos))

			if len(cactus) == 2:
				num = random.randint(0,5)
				if num < 4:
					pos = random.randint(gap_c, int(3*gap_c/2))
					cactus.append(Cactus(cactus[-1].x+cactus[-1].width+pos))			

				else:
					pos = random.randint(int(gap_c/2), int(2*gap_c/3))
					cactus.append(Cactus(cactus[-1].x+cactus[-1].width+pos))



		# aumenta a dificuldade a cada 50 pontos (velocidade do chão)
		inc_dif = False
		if int(score) % 50 == 0:
			if int(score) > p_score + 10:
				inc_dif = True
			p_score = int(score)
		if inc_dif == True:
			floor_v = floor_v + 1
			inc_dif = False

		# para sair
		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False
				quit()


		keys = pg.key.get_pressed()

		# aperte 's' para salvar o melhor
		if keys[pg.K_s]:
			print("Salvando...")
			filename = 'Dino_prime_{0}'.format(GEN)
			fit = []
			for g in ge:
				fit.append(g.fitness)

			winner = ge[np.argmax(fit)]

			with open(filename, "wb") as f:
				pickle.dump(winner, f)
				f.close()


		# aperte "q" pra matar todos os dinos
		if keys[pg.K_q]:
			for x, dino in enumerate(dinos): # x é posição na lista dinos
				dinos.pop(x)
				nets.pop (x)
				ge.pop(x)


		# checa o cactu mais proximo
		cac_ind = 0
		bird_ind = 0
		if len(dinos) > 0:
			if len(cactus) > 1 and dinos[0].x > cactus[0].x + cactus[0].img.get_width():
				cac_ind = 1
		else:
			# se não há dinos, acaba essa geração
			run = False

		score += 0.1
		for x, dino in enumerate(dinos):
			dino.move()


			ge[x].fitness = score # recompensa por estar vivo
			
			# tomada de decisão (info que entra)
			output = nets[x].activate((dino.y, cactus[cac_ind].width, cactus[cac_ind].height, floor_v,
										cactus[cac_ind].x-dino.x,
										abs(dino.y - cactus[cac_ind].height),
										abs(cactus[cac_ind].x - cactus[cac_ind+1].x),
										flock[bird_ind].y,
										flock[bird_ind].x - dino.x,
										dino.y - flock[bird_ind].y))

			# outputs é uma lista
			if output[0] > 0.5 and dino.jumpct == 0:
				dino.isLow = False
				dino.vel = -8
				dino.jump()
				dino.jumpct = 18
				ge[x].fitness -= 0.05
			if output[1] > 0.5 and dino.jumpct == 0:
				dino.isLow = False
				dino.vel = -10
				dino.jump()
				dino.jumpct = 20
				ge[x].fitness -= 0.05

			if output[2] > 0.5 and dino.jumpct == 0:
				dino.isLow = True
				ge[x].fitness -= 0.05
			else:
				dino.isLow = False


		add_bird = False
		rem_c = [] # lista de cactus para apagar
		rem_b = [] # lista de passaros para apagar
		rem_p = [] # lista de nuvens para apagar
		for cac in cactus:
			for x, dino in enumerate(dinos): # x é posição na lista dinos
				
				if cac.collide(dino): # se colide
					# mata dino
					dinos.pop(x)
					nets.pop (x)
					ge.pop(x)
				
				# se dino passou pelo cacto
				if not(cac.passed) and cac.x + cac.img.get_width() < dino.x:
					ge[x].fitness += 5
					cac.passed = True
			
			# checa se cacto está visivel
			if cac.x + cac.img.get_width() < 0:
					rem_c.append(cac)
				
			cac.move(floor_v)

		for bird in flock:
			for x, dino in enumerate(dinos): # x é posição na lista dinos
				
				if bird.collide(dino): # se colide
					# mata dino
					dinos.pop(x)
					nets.pop (x)
					ge.pop(x)
				
				# se dino passou
				if not(bird.passed) and bird.x + bird.img.get_width() < dino.x:
					ge[x].fitness += 5
					bird.passed = True
			
			# checa se passarp está visivel
			if bird.x + bird.img.get_width() < 0:
					rem_b.append(bird)
					add_bird = True
				
			bird.move(floor_v)


		puf_ct += 1
		for puf in clouds:
			if puf.x + puf.img.get_width() < 0:
				rem_p.append(puf)

			# move a uma fração da vel do fundo
			if puf_ct == 6:
				puf.move(floor_v)
		if puf_ct == 6:
			puf_ct = 0

		# remove quem já sumiu
		for r in rem_p:
			clouds.remove(r)
		for r in rem_c:
			cactus.remove(r)
		for r in rem_b:
			flock.remove(r)

		if len(clouds) <= 4:
			num = random.randint(2,8)
			while num > 0:
				gap_c = 600
				pos = random.randrange(0,gap_c)
				clouds.append(Cloud(WIN_WID+pos))
				num -= 1
				gap_c = gap_c+pos

		if add_bird:
			gap_b = int(3000*floor_v/10)
			pos = random.randrange(gap_b, 3*gap_b)
			flock.append(Bird(gap_b+pos))
			add_bird = False

		if score > b_score:
			b_score = score
		base.move(floor_v)
		redraw(win, dinos, cactus, flock, clouds, base, score, b_score)

	GEN += 1


# NEAT  
def run(config_path, load=False, save=True):
	# carrega configurações
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
								neat.DefaultSpeciesSet, neat.DefaultStagnation,
								config_path)
	
	
	if load:
		# recarregar população (todo o estado anterior)
		filename = 'dinos-65'
		p = neat.Checkpointer.restore_checkpoint(filename)
		global GEN
		GEN = p.generation
	else:
		# cria a população do config
		p = neat.Population(config)



	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	# metodo Checkpointer salva o estado da simulaçãp
	# automaticamente depois de tantas gerações
	p.add_reporter(neat.Checkpointer(25, filename_prefix='dinos-'))


	# roda e ao terminar te dá o genoma com melhor fit
	winner = p.run(main, 200)


	node_names = {0:'jump', 1:'high_jump', 2:'duck'}
	# desenha um genoma
	visualize.draw_net(config, winner, True, node_names=node_names, filename='dino_prime_genome')
	# plota estatisticas do processo de evolução
	visualize.plot_stats(stats, ylog=False, view=True,filename='dino_fit_evolve')
	# plota especiação?
	visualize.plot_species(stats, view=True)


	if save:
		# salvar o vencedor
		print("Salvando...")
		filename = 'Dino_prime_{0}'.format(GEN) 
		with open(filename, "wb") as f:
			pickle.dump(winner, f)
			f.close()
	
	quit()


if __name__ == "__main__":
	GEN = 0
	b_score = 0
	
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "dino_evolve_neat_config.txt")
	run(config_path, load=False, save=True)