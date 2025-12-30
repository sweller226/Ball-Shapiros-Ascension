import math
from random import randint, randrange
import pygame
from settings import *
from gameData import *
from support import *
from debug import debug

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprites, trackerHeight, camCenter):
        super().__init__()
        self.sprites = sprites
        self.surf = pygame.display.get_surface()
        self.pos = [x, y]

        self.image = pygame.image.load("./Graphics/Placeholder/Test-Ball.png").convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))

        self.velocityX = 0
        self.velocityY = 0
        self.gravity = 0.2
        self.originGravity = 0.2
        self.jumps = 0
        self.isClick = False
        self.jumpEnd = 0

        self.minJump = -0.1
        self.terminalVel = 20

        self.trailList = []

        self.camCenter = camCenter

        # Tracking Absolute Height
        self.tracker = layoutTile(100, trackerHeight, HeightTracker)
        self.playerHeight = self.pos[1] - self.tracker.pos[1]
        self.sprites["Layout"].add(self.tracker)

        self.cameraCorrection = self.tracker.pos[1]
        self.cameraCenter()
        self.cameraCorrection -= self.tracker.pos[1]
        self.tracker.pos[1] -= trackerHeight

    def cameraCenter(self):
        for Layer in self.sprites:             
            for sprite in self.sprites[Layer]:
                sprite.pos[1] -= self.pos[1] - self.camCenter
                sprite.rect.y = sprite.pos[1]
        self.pos[1] = self.camCenter
    
    def showPercentage(self):
        offset = -120
        percentage = math.floor((level.levelHeight*TILE_SIZE - self.playerHeight + offset)/(level.levelHeight*TILE_SIZE - 399*TILE_SIZE + offset)*100)
        debug(f"{percentage}%", 1100, 60)

    def update(self):
        self.velocityX = round(self.velocityX, 3)
        self.velocityY = round(self.velocityY, 3)

        self.jump()
        self.camera()
        self.collision()
        self.D_Crystal()
        # self.showPercentage()

        # Updating Absolute Height
        self.playerHeight = self.pos[1] - self.tracker.pos[1]
        save(self)

    def collision(self):
        self.vertical_collision()

        self.pos[0] += self.velocityX
        self.rect.x = self.pos[0]
        self.horizontal_collision()

        self.slopeCollision()

    def D_Crystal(self):
        for sprite in self.sprites["D_Crystal"]:
            if sprite.isAlive == False:
                sprite.reset()

            if sprite.rect.colliderect(self.rect) and sprite.isAlive:
                self.jumps = 1
                sprite.isAlive = False
                sprite.start = 0

    def camera(self):
        if self.pos[1] < HEIGHT*0.40 and self.velocityY < 0 or self.pos[1] > HEIGHT*0.76 and self.velocityY > 0:
            for Layer in self.sprites:
                if Layer != "Player":                
                    for sprite in self.sprites[Layer]:
                        sprite.pos[1] -= self.velocityY
                        sprite.rect.y = sprite.pos[1]
            for particle in self.trailList:
                particle.pos[1] -= self.velocityY
            
        else:
            self.pos[1] += self.velocityY
            self.rect.y = self.pos[1]

    def releaseMouse(self):
        if pygame.mouse.get_pressed()[0] and not self.isClick:
            self.jumpEnd = 0
            self.isClick = True
        elif self.isClick and not pygame.mouse.get_pressed()[0]:
            self.isClick = False
            return True
        return False

    def jump(self):
        jumpEndMax = 30
        if self.isClick:
            self.jumpEnd += 1

        yOffset = 100
        xOffset = 40
        pygame.draw.rect(self.surf, 'White', pygame.Rect(13+xOffset, 98+yOffset,50,304))
        pygame.draw.rect(self.surf, 'Green', pygame.Rect(15+xOffset,100+yOffset,46,300))
        pygame.draw.rect(self.surf, 'Black', pygame.Rect(15+xOffset,100+yOffset,46, jumpEndMax*10 - min(jumpEndMax*10, self.jumpEnd*10)))

        release = self.releaseMouse()

        cheatKey = pygame.key.get_pressed()[pygame.K_s]

        if cheatKey:
            release = True
            self.jumps = 1
            jumpEndMax = 30

        if self.jumps > 0 and release:
            self.jumps -= 1
            mousePos = pygame.mouse.get_pos()
            dist = (self.rect.centerx - mousePos[0], mousePos[1] - self.rect.centery)
            innitVelY = clamp_val(-12, 12, math.sqrt(abs(2*self.originGravity*dist[1])) * isNegative(dist[1]))

            if innitVelY == 0:
                innitVelY = self.minJump

            Time = innitVelY*-isNegative(innitVelY)/self.originGravity
            innitVelX = clamp_val(-10, 10, dist[0]/Time)

            innitVelY *= min(jumpEndMax, self.jumpEnd)/jumpEndMax
            self.velocityY = innitVelY
            
            self.velocityX = innitVelX

        self.gravityFunc()
        
    def gravityFunc(self):
        if self.velocityY < self.terminalVel:
            self.velocityY += self.gravity

    def boundaryCollisionCheck(self):
        if self.rect.left < SCREEN_WIDTH * 0.25:
            self.rect.left = SCREEN_WIDTH * 0.25 
            self.velocityX *= -1
            self.pos[0] = self.rect.x        

        elif self.rect.right > SCREEN_WIDTH * 0.75:
            self.rect.right = SCREEN_WIDTH * 0.75 
            self.velocityX *= -1
            self.pos[0] = self.rect.x

    def slopeCollision(self):
        for sprite in self.sprites["Slopes"]:
            if sprite.rect.colliderect(self.rect):
                if sprite.Facing == "Right":
                    dia_height = sprite.rect.height * (self.rect.right - sprite.rect.left) / sprite.rect.width
                else:
                    dia_height = -sprite.rect.height * (self.rect.left - sprite.rect.right) / sprite.rect.width
                D_rect_top =  max(sprite.rect.bottom - round(dia_height) - 3, sprite.rect.top)

                if abs(self.rect.bottom - D_rect_top) < 10 and not self.rect.bottom < D_rect_top:
                    if sprite.Facing == "Left":
                        if not self.velocityY < 0:
                            self.velocityY /= 2
                            self.velocityX += self.velocityY
                    else:
                        if not self.velocityY < 0:
                            self.velocityY /= 2
                            self.velocityX -= self.velocityY
                    self.rect.bottom = D_rect_top
                
                elif self.velocityY < 0 and abs(self.rect.top - sprite.rect.bottom) < 15:
                    self.rect.top = sprite.rect.bottom
                    self.velocityY *= -1
                
                elif sprite.Facing == "Right" and abs(self.rect.left - sprite.rect.right) < 15:
                    self.rect.left = sprite.rect.right
                    self.velocityX *= -1
                
                elif sprite.Facing == "Left" and abs(self.rect.right - sprite.rect.left) < 15:
                    self.rect.right = sprite.rect.left
                    self.velocityX *= -1
                
                elif self.rectInTriangle(sprite) and not self.rect.bottom < D_rect_top:
                    if abs(self.rect.centery - sprite.rect.bottom) < abs(self.rect.centery - D_rect_top):
                        self.rect.top = sprite.rect.bottom
                        self.velocityY *= -1

                    else:
                        self.velocityY /= 2
                        if sprite.Facing == "Left":
                            if not self.velocityY < 0:
                                self.velocityX += self.velocityY
                        else:
                            if not self.velocityY < 0:
                                self.velocityX -= self.velocityY
                        self.rect.bottom = D_rect_top

                self.pos[1] = self.rect.y
                self.pos[0] = self.rect.x

    def rectInTriangle(self, sprite):
        if sprite.Facing == "Right":
            x1 = sprite.rect.right
            x2 = sprite.rect.left
            x3 = sprite.rect.right

            y1 = sprite.rect.bottom
            y2 =  sprite.rect.bottom
            y3 = sprite.rect.top
        
        else:
            x1 = sprite.rect.left
            x2 = sprite.rect.right
            x3 = sprite.rect.left

            y1 = sprite.rect.top
            y2 =  sprite.rect.bottom
            y3 = sprite.rect.bottom   

        for i in range(self.rect.left, self.rect.right, 3):
            for j in range(self.rect.top, self.rect.bottom, 3):
                if inTriangle(x1, y1, x2, y2, x3, y3, i, j):
                    return True
        return False

    def horizontal_collision2(self, sprite):
        if sprite.rect.colliderect(self.rect):
            if self.rect.bottom > sprite.rect.top + 5:
                if self.rect.left < sprite.rect.right and self.velocityX > 0:
                    self.rect.right = sprite.rect.left
                    self.velocityX *= -sprite.XBounce

                elif self.rect.right > sprite.rect.left and self.velocityX < 0:
                    self.rect.left = sprite.rect.right
                    self.velocityX *= -sprite.XBounce
            self.pos[0] = self.rect.x
    
    def horizontal_collision(self):
        self.boundaryCollisionCheck()
        for sprite in self.sprites["Layout"]:
            self.horizontal_collision2(sprite)
        for sprite in self.sprites["Slime"]:
            self.horizontal_collision2(sprite) 

    def vertical_collision2(self, sprite):
        if sprite.rect.colliderect(self.rect):
            if self.velocityY > 0 and abs(self.rect.bottom - sprite.rect.top) < 20:
                if not sprite in self.sprites["Slime"]:
                    self.jumps = 1
                self.rect.bottom = sprite.rect.top

                # getting a nice bounce
                if self.velocityY < 3:
                    self.velocityY -= 1
                
                if self.velocityY > 0:
                    self.velocityY *= -sprite.YBounce
                else:
                    self.velocityY = 0

                # x velocity slowdown
                self.velocityX *= sprite.Friction

            elif self.velocityY < 0 and abs(self.rect.top - sprite.rect.bottom) < 20:
                self.rect.top = sprite.rect.bottom
                self.velocityY *= -sprite.YBounce

            self.pos[1] = self.rect.y
    
    def vertical_collision(self):
        for sprite in self.sprites["Layout"]:
            self.vertical_collision2(sprite)
        for sprite in self.sprites["Slime"]:
            self.vertical_collision2(sprite)
            

    def ambientParticles(self):
        if self.playerHeight < 535*TILE_SIZE:
            colour = "Yellow"
        elif self.playerHeight < 703*TILE_SIZE:
            colour = [3, 252, 252]
        elif self.playerHeight < 793*TILE_SIZE:
            colour = "Green"
        elif self.playerHeight < 909*TILE_SIZE:
            colour = "Red"
        else:
            colour = "White"

        if randint(1, 50) == 1:
            self.trailList.append(Particle([randint(0, SCREEN_WIDTH), randint(0, SCREEN_WIDTH)], self.surf, 5, 0.005, randint(1, 2), colour))
            
        for particle in self.trailList:
            if particle.index % 2 == 0:
                particle.pos[0] += randrange(5, 10) / 10
            else:
                particle.pos[0] -= randrange(5, 10) / 10
            particle.pos[1] -= 1
    
    def trail(self):
        self.trailList.append(Particle([self.pos[0]+15, self.pos[1]+16], self.surf, 15, 1.25))
        self.trailList.append(Particle([self.pos[0]+15-self.velocityX/2, self.pos[1]+16-self.velocityY/2], self.surf, 15, 1.25))
        self.ambientParticles()
        
        for particle in self.trailList:
            particle.draw()

            if particle.radius <= 1:
                self.trailList.remove(particle)
                del particle


class Particle:
    def __init__(self, pos, surface, radius, speed, index = 0, colour = "White"):
        self.radius = radius
        self.surf = surface
        self.pos = pos
        self.speed = speed
        self.index = index
        self.colour = colour

    def draw(self):
        pygame.draw.circle(self.surf, self.colour, self.pos, round(self.radius), 16)
        self.radius -= self.speed
        self.pos[0] -= self.speed/2
        self.pos[1] += self.speed/2
    
        
