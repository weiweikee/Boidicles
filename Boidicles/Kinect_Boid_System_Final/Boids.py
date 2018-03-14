import pygame
import numpy
import random
import copy
import sys
import math
import colorsys

from Boid import *

class Boids():
    # Boid System containing each boid
    def __init__(self, num, scale, width, height, controller=None):
        self.num = num
        self.scale = scale
        self.boids = []
        self.maxSpeed = 20 * self.scale
        self.maxForce = 2 * self.scale
        self.width = width
        self.height = height
        self.countLeft = 0
        self.countRight = 0
        self.textsurface0 = None
        self.textsurface1 = None
        self.textsurface2 = None
        self.textsurface3 = None
        self.textsurface4 = None
        self.textsurface5 = None
        self.textsurface6 = None
        self.textsurface7 = None
        self.goldren_ratio = 0.619033988749895
        if controller == None:
            self.controller = [True, True, True,
                               True, 1, False]
        else:
            self.controller = controller

    def makeBoid(self):
        maxSpeed = self.maxSpeed
        maxForce = self.maxForce
        num = self.num
        hue = (random.random() + self.goldren_ratio) % 1
        for i in range(num):
            pos = random.random() * self.width, random.random() * self.height
            saturation = random.uniform(0.3, 0.7)
            value = random.uniform(0.3, 0.7)
            color = colorsys.hsv_to_rgb(hue, saturation, value)
            color = color[0]*255, color[1]*255, color[2]*255
            # color = (random.random()*127 + 127, random.random()*127 + 127, random.random()*127 + 127)
            # if i % 2 == 0:
                # color = (random.randint(0, 255), random.randint(150, 255) , 0)
            # else:

                # color = (random.randint(0, 255), 90, 200)
            newBoid = Boid(pos, maxSpeed, maxForce,
                                   self.scale, self.controller, self.width, self.height, color)
            self.boids.append(newBoid)


    def update(self, target1, target2, obstacles):
        # Applied behavior for each boid
        for i in range(len(self.boids)):
            self.boids[i].applyBehaviors(self.boids, target1, target2, obstacles)
            self.boids[i].update(self.width, self.height)

    def addBoid(self, mouseVec):
        maxSpeed = self.maxSpeed
        maxForce = self.maxForce
        color = (200, 90, random.randint(0, 255))
        if len(self.boids)+1 % 2 == 0:
            color = (random.randint(0, 255), 90, 200)
        else:
            color = (200, 90, random.randint(0, 255))
        self.boids.append(Boid(mouseVec, maxSpeed, maxForce,
                               self.scale, self.controller, self.width, self.height, color))

    def draw(self, DISPLAY1, DISPLAY2, Menu, Hands, HandState, countLeft, countRight):
        for i in range(len(self.boids)):
            self.boids[i].dynamicDraw(DISPLAY1, self.boids, self.scale)
        if not Menu:
            self.textDraw(DISPLAY1, DISPLAY2, Hands, HandState, countLeft, countRight)

    def stateChange(self):
        # Change all controller
        for i in range(len(self.boids)):
            self.boids[i].controller = self.controller
    
    def textDraw(self, DISPLAY1, DISPLAY2, Hands, HandState, countLeft, countRight):
        myfont = pygame.font.SysFont('Century Gothic', 40)

        if (self.controller[0]):
            AlignColor = (255, 255, 255)
        else:
            AlignColor = (100, 100, 100)

        if (self.controller[1]):
            CohesionColor = (255, 255, 255)
        else:
            CohesionColor = (100, 100, 100)

        if (self.controller[2]):
            SeperationColor = (255, 255, 255)
        else:
            SeperationColor = (100, 100, 100)

        if (self.controller[3]):
            NoiseColor = (255, 255, 255)
        else:
            NoiseColor = (100, 100, 100)


        ArrowColor = (100, 100, 100)
        CircleColor = (100, 100, 100)
        DiamondColor = (100, 100, 100)
        paperColor = (100, 100, 100)
        PapertrailColor = (100, 100, 100)
        TrailColor = (100, 100, 100)

        if (self.controller[4] == 1):
            ArrowColor = (255, 255, 255)
            TrailColor = (100, 100, 100)
        elif (self.controller[4] == 2):
            ArrowColor = (255, 255, 255)
            TrailColor = (255, 255, 255)
        elif (self.controller[4] == 3):
            CircleColor = (255, 255, 255)
            TrailColor = (100, 100, 100)
        elif (self.controller[4] == 4):
            CircleColor = (255, 255, 255)
            TrailColor = (255, 255, 255)
        elif (self.controller[4] == 5):
            DiamondColor = (255, 255, 255)
            TrailColor = (100, 100, 100)
        elif (self.controller[4] == 6):
            DiamondColor = (255, 255, 255)
            TrailColor = (255, 255, 255)

        elif(self.controller[4] == 7):
            PapertrailColor = (255, 255, 255)


        alignText = "Alignment"
        cohesionText = "Cohesion"
        seperationText = "Seperation"
        noiseText = "Noise"
        arrowText = "Arrow"
        circleText = "Circle"
        diamondText = "Diamond"
        PaperTrailText = "Paper Trail"
        TrailText = "Trail"

        self.textsurface0 = myfont.render(alignText, True, AlignColor)
        self.textsurface1 = myfont.render(cohesionText, True, CohesionColor)
        self.textsurface2 = myfont.render(seperationText, True, SeperationColor)
        self.textsurface3 = myfont.render(noiseText, True, NoiseColor)
        self.textsurface4 = myfont.render(arrowText, True, ArrowColor)
        self.textsurface5 = myfont.render(circleText, True, CircleColor)
        self.textsurface6 = myfont.render(diamondText, True, DiamondColor)
        self.textsurface7 = myfont.render(PaperTrailText, True, PapertrailColor)
        self.textsurface8 = myfont.render(TrailText, True, TrailColor)
        
        if (self.checkOverlay(Hands[0], 40, 40, self.textsurface0) or 
           self.checkOverlay(Hands[1], 40, 40, self.textsurface0)):
            AlignColor = (255, 0, 0)
            self.textsurface0 = myfont.render(alignText, True, AlignColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
                            
        if (self.checkOverlay(Hands[0], 40, 40 + (70*1), self.textsurface1) or 
           self.checkOverlay(Hands[1], 40, 40 + (70*1), self.textsurface1)):
            CohesionColor = (255, 0, 0)
            self.textsurface1 = myfont.render(cohesionText, True, CohesionColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
   
        if (self.checkOverlay(Hands[0], 40, 40 + (70*2), self.textsurface2) or 
           self.checkOverlay(Hands[1], 40, 40 + (70*2), self.textsurface2)):
            SeperationColor = (255, 0, 0)
            self.textsurface2 = myfont.render(seperationText, True, SeperationColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
    
        if (self.checkOverlay(Hands[0], 40, 40 + (70*3), self.textsurface3) or 
            self.checkOverlay(Hands[1], 40, 40 + (70*3), self.textsurface3)):
            NoiseColor = (255, 0, 0)
            self.textsurface3 = myfont.render(noiseText, True, NoiseColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
        
        if (self.checkOverlay(Hands[0], 1650, 40, self.textsurface4) or 
            self.checkOverlay(Hands[1], 1650, 40, self.textsurface4)):
            ArrowColor = (255, 0, 0)
            self.textsurface4 = myfont.render(arrowText, True, ArrowColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
       
        if (self.checkOverlay(Hands[0], 1650, 40 + (70*1), self.textsurface5) or 
            self.checkOverlay(Hands[1], 1650, 40 + (70*1), self.textsurface5)):
            CircleColor = (255, 0, 0)
            self.textsurface5 = myfont.render(circleText, True, CircleColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
       
        if (self.checkOverlay(Hands[0], 1650, 40 + (70*2), self.textsurface6) or 
            self.checkOverlay(Hands[1], 1650, 40 + (70*2), self.textsurface6)):
            DiamondColor = (255, 0, 0)
            self.textsurface6 = myfont.render(diamondText, True, DiamondColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)
       
        if (self.checkOverlay(Hands[0], 1650, 40 + (70*3), self.textsurface7) or 
            self.checkOverlay(Hands[1], 1650, 40 + (70*3), self.textsurface7)):
            PapertrailColor = (255, 0, 0)
            self.textsurface7 = myfont.render(PaperTrailText, True, PapertrailColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)

        if (self.checkOverlay(Hands[0], 1650, 40 + (70*4), self.textsurface8) or 
            self.checkOverlay(Hands[1], 1650, 40 + (70*4), self.textsurface8)):
            TrailColor = (255, 0, 0)
            self.textsurface8 = myfont.render(TrailText, True, TrailColor)
            self.drawSelectionLoader(DISPLAY2, Hands, HandState, countLeft, countRight)

        # Left Menu
        if (self.textsurface0 != None):
            DISPLAY1.blit(self.textsurface0, (40, 40))
        if (self.textsurface1 != None):
            DISPLAY1.blit(self.textsurface1, (40, 40 + (70*1)))
        if (self.textsurface2 != None):
            DISPLAY1.blit(self.textsurface2, (40, 40 + (70*2)))
        if (self.textsurface3 != None):
            DISPLAY1.blit(self.textsurface3, (40, 40 + (70*3)))

        # Right Menu
        if (self.textsurface4 != None):
            DISPLAY1.blit(self.textsurface4, (1650, 40))
        if (self.textsurface5 != None):
            DISPLAY1.blit(self.textsurface5, (1650, 40 + (70*1)))
        if (self.textsurface6 != None):
            DISPLAY1.blit(self.textsurface6, (1650, 40 + (70*2)))
        if (self.textsurface7 != None):
            DISPLAY1.blit(self.textsurface7, (1650, 40 + (70*3)))
        if (self.textsurface8 != None):
            DISPLAY1.blit(self.textsurface8, (1650, 40 + (70*4)))

    
    def drawSelectionLoader(self, DISPLAY, Hands, HandState, countLeft, countRight):
        L_state, R_state = HandState
        if L_state == 3:
            rect_left = Hands[0][0], Hands[0][1], 100, 100
            pygame.draw.arc(DISPLAY, (255,0,255), rect_left, 
                        math.pi/4, math.pi*2*(countLeft/10)+math.pi/4, 10)
        elif R_state == 3:
            rect_right = Hands[1][0], Hands[1][1], 100, 100
            pygame.draw.arc(DISPLAY, (255,0,0), rect_right, 
                        math.pi/4, math.pi*2*(countRight/10)+math.pi/4, 10)
                        
    def checkOverlay(self, Hand, X, Y, surface):

        if (X <= Hand[0] <= X + surface.get_width() and
            Y <= Hand[1] <= Y + surface.get_height()):
                return True
        return False

    def randomColor(self):
        hue = (random.random() + self.goldren_ratio) % 1
        for i in range(len(self.boids)):
            saturation = random.uniform(0.3, 0.7)
            value = random.uniform(0.3, 0.7)
            color = colorsys.hsv_to_rgb(hue, saturation, value)
            color = color[0]*255, color[1]*255, color[2]*255
            self.boids[i].color = color

