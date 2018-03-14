import pygame
import random
import math

from Boid import *
from Boids import *
from Obstacles import *
from Path import *

class Menu(object):

    def __init__(self, DISPLAY, width, height):
        self.DISPLAY = DISPLAY
        num1 = random.randint(20, 40)
        scale1 = 30 / num1
        self.newBoidSystemMenu = Boids(num1, scale1, self.DISPLAY.get_width(), self.DISPLAY.get_height())
        self.newBoidSystemMenu.makeBoid()
        self.drawText = "DRAW"
        self.simulateText = "SIMULATE"
        self.tol = 150
        self.countLeft = 0
        self.countRight = 0
        self.width = width
        self.height = height
        
    def drawMenu(self, left_hand, right_hand):
        myfont = pygame.font.SysFont('Century Gothic', 80, True)
        instructionFont = pygame.font.SysFont('Century Gothic', 40, True)

        self.drawBoid((left_hand[0], right_hand[0]), (left_hand[1], left_hand[1]))
        colors1 = (255, 255, 255)
        colors2 = (255, 255, 255)
       
        rect = left_hand[0][0], left_hand[0][1], 100, 100
        if (self.width/2 - self.tol <= left_hand[0][0] <= self.width/2 + self.tol and
            self.height/2 - 150 - self.tol <= left_hand[0][1] <= self.height/2 -150 + self.tol):
                colors1 = (255, 255, 0)
                if left_hand[1] == 3:
                    pygame.draw.arc(self.DISPLAY, (255,0,255), rect, 
                                math.pi/4, math.pi*2*(self.countLeft/10)+math.pi/4, 10)
        if (self.width/2 - self.tol <= left_hand[0][0] <= self.width/2 + self.tol and
            self.height/2 + 150 - self.tol <= left_hand[0][1] <= self.height/2 + 150 + self.tol):
                colors2 = (255, 255, 0)
                if left_hand[1] == 3:
                    pygame.draw.arc(self.DISPLAY, (255,0,255), rect, 
                                math.pi/4, math.pi*2*(self.countLeft/10)+math.pi/4, 10)
    
        rect = right_hand[0][0], right_hand[0][1], 100, 100
        if (self.width/2 - self.tol <= right_hand[0][0] <= self.width/2 + self.tol and
            self.height/2 - 150 - self.tol <= right_hand[0][1] <= self.height/2 - 150 + self.tol):
                colors1 = (255, 255, 0)
                if right_hand[1] == 3:
                    pygame.draw.arc(self.DISPLAY, (255,0,0), rect, 
                                math.pi/4, math.pi*2*(self.countRight/10)+math.pi/4, 10)
                                
        if (self.width/2 - self.tol <= right_hand[0][0] <= self.width/2 + self.tol and
            self.height/2 + 150 - self.tol <= right_hand[0][1] <= self.height/2 + 150 + self.tol):
                colors2 = (255, 255, 0)
                if right_hand[1] == 3:
                    pygame.draw.arc(self.DISPLAY, (255,0,0), rect, 
                                math.pi/4, math.pi*2*(self.countRight/10)+math.pi/4, 10)
        
        textDraw = myfont.render(self.drawText, True, colors1)
        textSimulate = myfont.render(self.simulateText, True, colors2)

        instruction1 = "Use LEFT and RIGHT Hand"
        instruction2 = "to move around the screen"
        instruction3 = "and make a FIST for 10 seconds to select Options"
        instructionSurface1 = instructionFont.render(instruction1, True, (255, 255, 255))
        instructionSurface2 = instructionFont.render(instruction2, True, (255, 255, 255))
        instructionSurface3 = instructionFont.render(instruction3, True, (255, 255, 255))

        self.DISPLAY.blit(textDraw, (self.width/2-textDraw.get_width()/2, 
                                          (self.height/2- 150)-textDraw.get_height()/2))
        
        self.DISPLAY.blit(textSimulate, (self.width/2-textSimulate.get_width()/2, 
                                          (self.height/2 + 150)-textSimulate.get_height()/2))

        self.DISPLAY.blit(instructionSurface1, (self.width/2-instructionSurface1.get_width()/2, 
                                          (self.height/2 + 250)-instructionSurface1.get_height()/2))
        self.DISPLAY.blit(instructionSurface2, (self.width/2-instructionSurface2.get_width()/2, 
                                          (self.height/2 + 300)-instructionSurface2.get_height()/2))
        self.DISPLAY.blit(instructionSurface3, (self.width/2-instructionSurface3.get_width()/2, 
                                          (self.height/2 + 350)-instructionSurface3.get_height()/2))

    
                
    def drawBoid(self, Hands, HandState):
        self.newBoidSystemMenu.update(None, None, [])
        self.newBoidSystemMenu.draw(self.DISPLAY, self.DISPLAY, True, Hands, HandState, 0, 0)
        
    def checkHand(self, LeftHand, RightHand, X, Y):
        sec = 10
        if LeftHand[1] == 3:
            if (X - self.tol <= LeftHand[0][0] <= X + self.tol and
                Y - self.tol <= LeftHand[0][1] <= Y + self.tol):
                self.countLeft +=1
        else:
            self.countLeft = 0
            
        if RightHand[1] == 3:
            if (X - self.tol <= RightHand[0][0] <= X + self.tol and
                Y - self.tol <= RightHand[0][1] <= Y + self.tol):
                self.countRight +=1
        else:
            self.countRight = 0
                
        if self.countLeft >= sec or self.countRight >= sec:
            self.countLeft = 0
            self.countRight = 0
            return True

        else: return False
    
        
    
