# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 18:16:49 2020

@author: medoug
"""
import pygame

pygame.init()

# dimensões da janela do jogo
winwid, winlen = 500, 480
win = pygame.display.set_mode((winwid,winlen))
# nome da janela
pygame.display.set_caption('Basic game')

# carregar sprites do jogo
walkR = [pygame.image.load('Game/R1.png'), pygame.image.load('Game/R2.png'), pygame.image.load('Game/R3.png'), pygame.image.load('Game/R4.png'),pygame.image.load('Game/R5.png'), pygame.image.load('Game/R6.png'), pygame.image.load('Game/R7.png'), pygame.image.load('Game/R8.png'),pygame.image.load('Game/R9.png')]
walkL = [pygame.image.load('Game/L1.png'), pygame.image.load('Game/L2.png'), pygame.image.load('Game/L3.png'), pygame.image.load('Game/L4.png'),pygame.image.load('Game/L5.png'), pygame.image.load('Game/L6.png'), pygame.image.load('Game/L7.png'), pygame.image.load('Game/L8.png'),pygame.image.load('Game/L9.png')]
bg = pygame.image.load('Game/bg.jpg')
char = pygame.image.load('Game/standing.png')

clock = pygame.time.Clock()
#bsound = pygame.mixer.Sound('Game/bullet.mp3') # som de tiro
#hsound = pygame.mixer.Sound('Game/hit.mp3') # som de hit

music = pygame.mixer.music.load('Game/music.mp3')
pygame.mixer.music.play(-1) # -1 é pra tocar continuamente

score = 0

class player():
    def __init__(self,x,y,width,height):
        # atributos do personagem
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 5
        self.isjump = False
        self.left = False
        self.right = False
        self.walkct = 0
        self.jumpct = 10
        self.stands = True
        self.hitbox = (self.x+20, self.y, 28, 60)
        
    def draw(self,win):
        # desenhar o personagem
        if self.walkct+1>=27: # 27 frames/s
            self.walkct = 0
        
        if not(self.stands): # se anda
            if self.left:
                win.blit(walkL[self.walkct//3], (self.x,self.y)) # int div //
                self.walkct += 1
            elif self.right:
                win.blit(walkR[self.walkct//3], (self.x,self.y))
                self.walkct += 1
        else: # se esta parado
            if self.right:
                win.blit(walkR[0], (self.x,self.y))
            else:
                win.blit(walkL[0], (self.x,self.y))
        self.hitbox = (self.x+20, self.y, 28, 60)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) # Desenha a caixa

    # jogador é acertado        
    def hit(self):
        self.x = 60
        self.y = 410
        self.isjump = False
        self.jumpct = 10
        self.walkct = 0
        font1 = pygame.font.SysFont('comicsans', 100)
        text = font1.render('DEAD', 1, (255,0,0))
        win.blit(text, (winwid/2 - text.get_width()/2, winlen/2))
        pygame.display.update()
        i = 0
        while i < 200:
            pygame.time.delay(10)
            i += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    i = 201
                    pygame.quit()
                    

# projéteis
class proj():
    def __init__(self,x,y,radius,color,facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.vel = 8*facing
        
    def draw(self,win):
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius)

# Inimigo
class enemy():
    walkR = [pygame.image.load('Game/R1E.png'), pygame.image.load('Game/R2E.png'), pygame.image.load('Game/R3E.png'), pygame.image.load('Game/R4E.png'),pygame.image.load('Game/R5E.png'), pygame.image.load('Game/R6E.png'), pygame.image.load('Game/R7E.png'), pygame.image.load('Game/R8E.png'),pygame.image.load('Game/R9E.png'),pygame.image.load('Game/R10E.png'),pygame.image.load('Game/R11E.png')]
    walkL = [pygame.image.load('Game/L1E.png'), pygame.image.load('Game/L2E.png'), pygame.image.load('Game/L3E.png'), pygame.image.load('Game/L4E.png'),pygame.image.load('Game/L5E.png'), pygame.image.load('Game/L6E.png'), pygame.image.load('Game/L7E.png'), pygame.image.load('Game/L8E.png'),pygame.image.load('Game/L9E.png'),pygame.image.load('Game/L10E.png'),pygame.image.load('Game/L11E.png')]
    
    def __init__(self, x, y, width, height, end):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.end = end
        self.path = [self.x, self.end]
        self.walkct = 0
        self.vel = 3
        self.hitbox = (self.x+17, self.y+2, 31, 57)
        self.health = 9
        self.visible = True
    
    def draw(self,win):
        self.move()
        if self.visible:
            if self.walkct +1 >= 33: # 33//3=11 sprites
                self.walkct = 0
                
            if self.vel > 0:
                win.blit(self.walkR[self.walkct//3], (self.x, self.y))
                self.walkct += 1
            else:
                win.blit(self.walkL[self.walkct//3], (self.x, self.y))
                self.walkct += 1
            pygame.draw.rect(win, (255,0,0), (self.hitbox[0], self.hitbox[1]-15, 50, 10))
            pygame.draw.rect(win, (0,180,0), (self.hitbox[0], self.hitbox[1]-15, 50 - (50/9*(9-self.health)), 10))
            self.hitbox = (self.x+17, self.y+2, 31, 57)
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) # Desenha a caixa
    
    def move(self):
        if self. vel > 0:
            if self.x + self.vel < self.path[1]:
                self.x += self.vel
            else:
                self.vel = self.vel*-1
                self.walkct = 0
        else:
            if self.x - self.vel > self.path[0]:
                self.x += self.vel
            else:
                self.vel = self.vel*-1
                self.walkct = 0
    
    def hit(self):
        if self.health > 0:
            self.health -= 1
        else:
            self.visible = False
        


# desenhar o mundo
def redraw():
    win.blit(bg, (0,0)) # desenha o fundo
    text = font.render('Score: '+ str(score), 1, (0,0,0)) # pontuação
    win.blit(text, (350,10))
    man.draw(win) # o jogador
    goblin.draw(win) # o inimigo
    for bullet in bullets:
        bullet.draw(win) # os tiros
        
    pygame.display.update()


# loop principal
font = pygame.font.SysFont('comicsans', 30, bold=True)
man = player(60,410,64,64)
bullets = []
shoots = 0 # cooldown do tiro
goblin = enemy(100, 410, 64, 64, 450)
run = True
while run:
    # frames/s
    clock.tick(27)
    
    # personagem acertado
    if goblin.visible:
        if man.hitbox[1] < goblin.hitbox[1]+goblin.hitbox[3] and man.hitbox[1] + man.hitbox[3] > goblin.hitbox[1]:
            if man.hitbox[0] + man.hitbox[2] > goblin.hitbox[0] and man.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]:
                man.hit()
                score -= 5
                #hsound.play()
    
    if shoots > 0:
        shoots +=1
    if shoots > 4:
        shoots = 0
    
    # checa os eventos do jogo
    for event in pygame.event.get():
        # fechar
        if event.type == pygame.QUIT:
            run = False
           
    # Tiro
    for bullet in bullets:
        # acertar
        if goblin.visible:
            if bullet.y - bullet.radius < goblin.hitbox[1]+goblin.hitbox[3] and bullet.y + bullet.radius > goblin.hitbox[1]:
                if bullet.x + bullet.radius > goblin.hitbox[0] and bullet.x - bullet.radius < goblin.hitbox[0] + goblin.hitbox[2]:
                    #hsound.play()
                    goblin.hit()
                    score += 1
                    bullets.pop(bullets.index(bullet))
        
        # movimento
        if bullet.x < winwid and bullet.x > 0:
            bullet.x += bullet.vel
        else:
            bullets.pop(bullets.index(bullet))
    
    # comandos
    keys = pygame.key.get_pressed()
    
    # tiro
    if keys[pygame.K_r] and shoots == 0:
        # som
        #bsound.play()
        # direção
        if man.left:
            facing = -1
        else:
            facing = 1
        
        if len(bullets) < 5: # limite de tiros
            # adiciona objeto à lista
            bullets.append(proj(round(man.x + man.width//2), round(man.y + man.height//2), 5,(0,0,255), facing))
            shoots = 1
    
    # andar
    if keys[pygame.K_a] and man.x > man.vel:
        man.x -= man.vel
        man.left = True
        man.right = False
        man.stands = False
    elif keys[pygame.K_d] and man.x < winwid - man.width - man.vel:
        man.x += man.vel
        man.left = False
        man.right = True
        man.stands = False
    else:
        man.stands = True
        man.walkct = 0
    
    if not (man.isjump):
        # se pular
        if keys[pygame.K_SPACE]:
            man.isjump = True
            man.right = False
            man.left = False
            man.walkct = 0
    else:
        if man.jumpct >= -10:
            neg = 1
            if man.jumpct < 0:
                neg = -1
            man.y -= (man.jumpct**2)*0.5*neg
            man.jumpct -= 1
        else:
            man.isjump = False
            man.jumpct = 10
    
    redraw()


pygame.quit()
