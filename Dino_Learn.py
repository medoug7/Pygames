
#@author: medoug7

import numpy as np
import pygame as pg
import time
import os
import random
import gzip

import logging
import os
# pra silenciar os avisos CUDA do tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(logging.FATAL)

try:
	import cPickle as pickle  # pylint: disable=import-error
except ImportError:
	import pickle  # pylint: disable=import-error

from dino_assets import Dino, Cactus, Bird, Cloud, Base, floor

from dino_learn_reinf_structure import Agent


pg.font.init()
FONT = pg.font.SysFont('comicsans', 30)


WIN_WID = 700
WIN_HEI = 300


# desenhar o mundo
def redraw(win, dino, cactus, flock, clouds, base, score, b_score, EPI):
	win.fill((255,255,255)) # fundo branco

	base.draw(win)
	for puf in clouds:
		puf.draw(win)
	for cac in cactus:
		cac.draw(win)
	for bird in flock:
		bird.draw(win)
	
	dino.draw(win)

	text = FONT.render('score: '+ str(int(score)), 0, (100,100,100)) # pontuação
	win.blit(text, (WIN_WID - 10 - text.get_width(), 10))

	text = FONT.render('best: '+ str(int(b_score)), 0, (100,100,100)) # pontuação
	win.blit(text, (WIN_WID - 10 - text.get_width(), 40))

	text = FONT.render('episode: ' +str(EPI), 0, (100,100,100))
	win.blit(text, (10, 10))

	pg.display.update()



# o jogo em si
def main(agent, n_games, train_rate, up_rate, have_bird=True, train=False):
	b_score = 0 # melhor pontuação
	scores = []
	avg_scores = []
	
	for EPI in range(1, n_games, 1):
		floor_v = 10

		base = Base(floor)
		gap_c = 500
		gap_b = 3000

		dino = Dino(80, floor - 40)

		pos = random.randint(0,gap_c/2)
		cactus = [Cactus(gap_c+pos),Cactus(2*gap_c+pos)]	
		flock = [Bird(random.randint(gap_b-500, gap_b+500))]
		clouds =[Cloud(random.randrange(0, WIN_WID)),Cloud(random.randrange(0, WIN_WID))]
		puf_ct = 0

		win = pg.display.set_mode((WIN_WID, WIN_HEI))
		pg.display.set_caption('Dino Learning')
		clock = pg.time.Clock()
		score = 0
		p_score = 0
		pass_ct = 0
		pass_bd = 0
		done = False

		# usar pra contar o intervalo de tempo antes de cada treino
		batch = 0

		# checa o cactu mais proximo
		cac_ind = 0
		bird_ind = 0
		if len(cactus) > 1 and dino.x > cactus[0].x + cactus[0].img.get_width():
			cac_ind = 1

		# estado atual
		state = np.array([dino.y, floor_v, cactus[cac_ind].width, cactus[cac_ind].height,
							cactus[cac_ind].x-dino.x, abs(dino.y - cactus[cac_ind].height),
							abs(cactus[cac_ind].x - cactus[cac_ind+1].x), flock[bird_ind].y, 
							flock[bird_ind].x - dino.x, dino.y - flock[bird_ind].y])


		if train:
			# atualiza a rede alvo
			if EPI % up_rate == 0:
				agent.update_aim()

			# atualiza a taxa de aprendizagem	
			'''if EPI % 100 == 0:
				#print('update')
				agent.update_lr(agent.lr/2)
			'''


		while not done:
			clock.tick(30)
			just_jumped = 0 # 0=no chão, 1=acaba de pula, 2=acaba de cair
			reward = 0


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
					done = True
					quit()


			keys = pg.key.get_pressed()

			# aperte 's' para salvar o melhor
			if keys[pg.K_s]:
				print("Salvando...")
				agent.save()


			# tomada de decisão
			# action é um int (caso discreto)
			action = agent.choose(state)

			# faz nada
			if action == 0:
				dino.isLow = False
			# pulo baixo
			elif action == 1 and dino.jumpct == 0:
				dino.isLow = False
				dino.vel = -8
				dino.jump()
				dino.jumpct = 18
				just_jumped = 1
			# pulo alto
			elif action == 2 and dino.jumpct == 0:
				dino.isLow = False
				dino.vel = -10
				dino.jump()
				dino.jumpct = 20
				just_jumped = 1
			# abaixa
			elif action == 3 and dino.jumpct == 0:
				dino.isLow = True

			dino.move()


			add_bird = False
			rem_c = [] # lista de cactus para apagar
			rem_b = [] # lista de passaros para apagar
			rem_p = [] # lista de nuvens para apagar
			for cac in cactus:
				if cac.collide(dino): # se colide
					# acaba o episódio
					done = True
				
				# se dino passou pelo cacto
				if not(cac.passed) and cac.x + cac.img.get_width() + 5 < dino.x:
					cac.passed = True
					pass_ct = 1
				
				# checa se cacto está visivel
				if cac.x + cac.img.get_width() < 0:
					rem_c.append(cac)
					
				cac.move(floor_v)

			for bird in flock:
				if have_bird:				
					if bird.collide(dino): # se colide
						# acaba o episódio
						done = True
				
				# se dino passou
				if not(bird.passed) and bird.x + bird.img.get_width() + 5 < dino.x:
					bird.passed = True
					pass_bd = 1
				
				# checa se passaro está visivel
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


			# checa o cactu mais proximo
			cac_ind = 0
			bird_ind = 0
			if len(cactus) > 1 and dino.x > cactus[0].x + cactus[0].img.get_width():
				cac_ind = 1

			# estado próximo estado
			n_state = np.array([dino.y, floor_v, cactus[cac_ind].width, cactus[cac_ind].height,
								cactus[cac_ind].x-dino.x, abs(dino.y - cactus[cac_ind].height),
								abs(cactus[cac_ind].x - cactus[cac_ind+1].x), flock[bird_ind].y, 
								flock[bird_ind].x - dino.x, dino.y - flock[bird_ind].y])


			# só vamos lembrar de estados que o agente tem agência (pode agir)
			# enquanto o dino está no ar ele não consegue fazer nada
			if just_jumped == 1:
				j_state = state
				j_action = action
				#print('pula')

			elif dino.jumpct == 1:
				just_jumped = 2
				#print('cai')


			if train:
				# se morre
				if done:
					reward = -100
					pass_ct = 0
					#print('ouch, reward:', reward)

					# se morre no ar
					if dino.isJump:
						#print('cai')
						agent.remember(j_state, j_action, reward, state, done)
					
					# se morre1 no chão
					else:
						#print('bati')
						agent.remember(state, action, reward, n_state, done)
					
				# se está no chão
				elif not dino.isJump:

					# se passa pelo cactu (necessariamente depois de um pulo)
					if pass_ct == 1:
						reward = 100
						agent.remember(j_state, j_action, reward, state, done)
						pass_ct = 0
						#print('pass, reward:', reward)


					elif have_bird:
						# se passa pelo passaro pulando
						if pass_bd == 1 and just_jumped == 2:
							reward = 100
							# assim ele vai lembrar do estado antes de pular e da ação pular, e vai 
							# relacionar com o próximo estado sendo de sucesso
							agent.remember(j_state, j_action, reward, state, done)
							pass_bd = 0
							#print('pass, reward:', reward)

						# se passa pelo passaro andando ou abaixando
						elif pass_bd == 1:
							reward = 100
							agent.remember(state, action, reward, n_state, done)
							pass_bd = 0
							#print('pass, reward:', reward)

						# se nada acontece
						else:
							#print('pass', reward)
							if agent.mem.mem_ct < int(agent.batch_size*5):
								agent.remember(state, action, reward, n_state, done)

							# quando a memória tiver enchendo guardar menos lembranças de 
							# quando nada acontece
							elif batch % 2 == 0:
								agent.remember(state, action, reward, n_state, done)


					# se nada acontece
					else:
						#print('pass', reward)

						if agent.mem.mem_ct < int(agent.batch_size*5):
							agent.remember(state, action, reward, n_state, done)

						# quando a memória tiver enchendo guardar menos lembranças de 
						# quando nada acontece
						elif batch % 2 == 0:
							agent.remember(state, action, reward, n_state, done)

				

				# treina depois de quantas adições de memória
				batch += 1
				# se alcançar 200 pontos, pausar o treino pra não desregular a rede
				if batch == train_rate and score<200:
					agent.learn_D() # treina simple Double Deep-QL
					batch = 0


			if score > b_score:
				b_score = score


			# move as coisas
			score += 0.1
			base.move(floor_v)
			redraw(win, dino, cactus, flock, clouds, base, score, b_score, EPI)

			state = n_state

		scores.append(int(score))
		avg_scores.append(np.mean(scores[max(0, EPI-10):EPI+1]))
		print(EPI, '- score:', scores[-1],'- avg:', np.round(avg_scores[-1],3), '- eps:', np.round(agent.eps,4))




	return scores, avg_scores



# train 
def run(n_games, load=False, save=True, tune=False, have_bird=True):

	if tune:
		# testar diferentes hiperparâmetros
		batch_sizes = [256, 512]
		train_rates = [4]
		up_rates = [8, 12]

		history = []

		print('Tunando Dino')
		for u in up_rates:
			for t in train_rates:
				for b in batch_sizes:

					agent = Agent(lr=0.001, gamma=0.99, input_dim=10, n_actions=4, mem_size=10000,
									batch_size=b, eps=1, eps_dec=0.996, eps_min=0.01, fname='Dino_smart.h5')

					print('\nbatch_size:',b, '- train_rate:', t, '- up_rate:', u)

					start = time.time()				

					# roda o jogo
					avgs = main(agent, n_games, t, u, have_bird, train=True)[1]
					
					total = time.time() - start
					print('time:',round(total,3))
					history.append([total,b,t,u,np.array((avgs))])



		with open ("dino_tune_DD_history.txt", 'wb') as fp:
			pickle.dump(history, fp)


	# testar aprendizado estático
	else:
		# carregar
		if load:
			print('Carregando Dino')
			agent = Agent(lr=0.001, gamma=0.99, input_dim=10, n_actions=4, mem_size=10000,
							batch_size=256, eps=1, eps_dec=0.996, eps_min=0.01, fname='Dino_smart_DD_273_nobird.h5')

			agent.load()
			agent.eps = agent.eps_min

		# começar outro
		else:
			print('Criando Dino')
			agent = Agent(lr=0.001, gamma=0.99, input_dim=10, n_actions=4, mem_size=10000,
							batch_size=256, eps=1, eps_dec=0.996, eps_min=0.01, fname='Dino_smart.h5')

		train_rate = 4
		up_rate = 12
		start = time.time()

		# roda o jogo
		scores = main(agent, n_games, train_rate, up_rate, have_bird, train=True)[1]

		total = time.time() - start
		print('time:',round(total,3))

		with open ("dino_p_history.txt", 'wb') as fp:
			pickle.dump(scores, fp)


	if save:
		# salvar o vencedor
		print("Salvando...")
		agent.save()

	quit()


if __name__ == "__main__":

	# nº de jogos, carregar dino salvo, salvar no final do treino
	# tunar hyperparâmetros, levar o pássaro em consideração
	run(n_games=500, load=False, save=False, tune=False, have_bird=False)
