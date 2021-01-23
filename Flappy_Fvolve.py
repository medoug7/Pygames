# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 17:34:34 2020

@author: medou
"""

import pygame as pg
import neat
import time
import os
import random
pg.font.init()

WIN_WID = 500
WIN_HEI = 800

BIRD_IMGS = [pg.transform.scale2x(pg.image.load('flappy/bird1.png')), pg.transform.scale2x(pg.image.load('flappy/bird2.png')), pg.transform.scale2x(pg.image.load('flappy/bird3.png'))]
PIPE_IMG = pg.transform.scale2x(pg.image.load('flappy/pipe.png'))
BASE_IMG = pg.transform.scale2x(pg.image.load('flappy/base.png'))
BG_IMG = pg.transform.scale2x(pg.image.load('flappy/bg.png'))

FONT = pg.font.SysFont('comicsans',50)

GEN = 0

# passaro
class Bird():
    IMGS = BIRD_IMGS
    MAX_ROT = 25
    ROT_VEL = 20
    ANIM_TIME = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_ct = 0
        self.vel = 0
        self.height = self.y
        self.img_ct = 0
        self.img = self.IMGS[0]
        
        
    def jump(self):
        self.vel = -10.5
        self.tick_ct = 0
        self.height = self.y
        
    # mover
    def move(self):
        self.tick_ct += 1
        
        d = self.vel*self.tick_ct + 1.3*self.tick_ct**2
        
        # vel terminal
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        
        self.y = self.y + d
        
        # checar a posição em é podemos inclinar o passaro
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
            
    # desenha o passaro
    def draw(self,win):
        self.img_ct += 1
        
        if self.img_ct < self.ANIM_TIME:
            self.img = self.IMGS[0]
        elif self.img_ct < self.ANIM_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_ct < self.ANIM_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_ct < self.ANIM_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_ct < self.ANIM_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_ct = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_ct = self.ANIM_TIME*2
        
        rotate_img = pg.transform.rotate(self.img, self.tilt)
        new_rect = rotate_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotate_img, new_rect.topleft)
            
    # máscara para colisões mais precisas        
    def get_mask(self):
        return pg.mask.from_surface(self.img)
        
    
        

class Pipe():
    GAP = 200
    VEL = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pg.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOT = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
    # altura
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    # mover
    def move(self):
        self.x -= self.VEL
        
    # desenha
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOT, (self.x, self.bottom))

    # colisões
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pg.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pg.mask.from_surface(self.PIPE_BOT)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        
        if t_point or b_point:
            return True
        
        return False



class Base():
    VEL = 5
    WID = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WID
        
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WID < 0:
            self.x1 = self.x2 + self.WID
        if self.x2 + self.WID < 0:
            self.x2 = self.x1 + self.WID
        
    def draw(self,win):
        win.blit(self.IMG, (self.x1,self.y))
        win.blit(self.IMG, (self.x2,self.y))
      

def redraw(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
        
    text = FONT.render('Score: ' +str(score), 1, (255,255,255))
    win.blit(text, (WIN_WID - 10 - text.get_width(), 10))
    
    text = FONT.render('Gen: ' +str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))
    
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pg.display.update()


# transformar main numa função fitness
def main(genomes, config):
    global GEN
    GEN += 1
    
    # define as redes que competem
    nets = []
    ge = []
    birds = []
    
    # genomas é um tuple (indice, genoma)
    for _,g in genomes:
        
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)
    
    
    base = Base(730)
    pipes = [Pipe(600)]
    win = pg.display.set_mode((WIN_WID, WIN_HEI))
    run = True
    
    clock = pg.time.Clock()
    score = 0
    
    while run:
        clock.tick(30)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()

        # checa o cano mais proximo
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                   pipe_ind = 1
        else:
            # se não há passaros, acaba essa geração
            run = False
        
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.05 # recompensa por estar vivo
            
            # tomada de decisão (info que entra)
            output = nets[x].activate((bird.y,
                                       abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))
            # outputs é uma lista
            if output[0] > 0.5:
                bird.jump()
        

        add_pipe = False
        rem = [] # lista de canos para apagar
        for pipe in pipes:
            for x, bird in enumerate(birds): # x é posição na lista birds
                
                if pipe.collide(bird): # se colide
                    ge[x].fitness -= 1 # remover pontos
                    # mata pássaro
                    birds.pop(x)
                    nets.pop (x)
                    ge.pop(x)
                
                # se passaro passou pelo cano
                if not(pipe.passed) and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                    score += 1
            
            # checa se cano está visivel
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)
                
            pipe.move()

        for r in rem:
            pipes.remove(r)
            
        if add_pipe:
            # recompensa os bixos
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
        
        for x, bird in enumerate(birds):
            # checa se o bixo caiu no chão
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
            
        base.move()
        redraw(win, birds, pipes, base, score, GEN)
        
          
# NEAT  
def run(config_path):
    # carrega configurações
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    
    # roda e ao terminar te dá o melhor fit
    winner = p.run(main,50)
    
    # salvar o vencedor
    #import pickle
    
    quit()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "flappy_neat_config.txt")
    run(config_path)