from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random
import copy
import colorsys
from Menu import *
from Boid import *
from Boids import *
from Obstacles import *


def drawKinect(surface, L, R):
    left = pygame.image.load('left_hand.png')
    right = pygame.image.load('right_hand.png')
    Lx, Ly = L
    Rx, Ry = R
    left = pygame.transform.scale(left, (200, 200))
    right = pygame.transform.scale(right, (200,200))
    surface.blit(left, (Lx-left.get_width()/2, Ly-left.get_height()/2))
    surface.blit(right, (Rx-right.get_width()/2, Ry-right.get_height()/2))
    pygame.draw.circle(surface, (0, 255, 255), (int(Lx), int(Ly)), 20, 0)
    pygame.draw.circle(surface, (255, 255, 0), (int(Rx), int(Ry)), 20, 0)
    
def trackKinect(kinect):
    L = None
    R = None
    if kinect.has_new_body_frame():
        bodies = kinect.get_last_body_frame()
        if bodies is not None:
            for i in range(0, kinect.max_body_count):
                body = bodies.bodies[i]
                if not body.is_tracked:
                    continue
                joints = body.joints
                colorJoints = kinect.body_joints_to_color_space(joints)
                if joints[PyKinectV2.JointType_HandRight].TrackingState == PyKinectV2.TrackingState_Tracked:
                    Rx = colorJoints[PyKinectV2.JointType_HandRight].x 
                    Rx = ((Rx-550)/(1920-550)) * 3000
                    Ry = colorJoints[PyKinectV2.JointType_HandRight].y /1080
                    Ry *= 1500
                    Rs = body.hand_right_state
                    R = Rx, Ry
 
                    
                if joints[PyKinectV2.JointType_HandLeft].TrackingState == PyKinectV2.TrackingState_Tracked:
                    Lx = colorJoints[PyKinectV2.JointType_HandLeft].x 
                    Lx = ((Lx-550)/(1920-550)) * 3000
                    Ly = colorJoints[PyKinectV2.JointType_HandLeft].y / 1080 
                    Ly *= 1500
                    Ls = body.hand_left_state
                    L = Lx, Ly    

    if L != None and R != None:
        return L, R, Ls, Rs

def run():
    pygame.init()
    pygame.font.init()
    done = False
    screen_width = 1920
    screen_height = 1080
    scale = 1
    screen = pygame.display.set_mode((screen_width, screen_height),
                                            pygame.HWSURFACE | pygame.DOUBLEBUF, 32)
    clock = pygame.time.Clock()
    kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | FrameSourceTypes_Body)
    bodies = None
    
    frame_surface = pygame.Surface((screen_width, screen_height), 0, 32)
    frame_marker = pygame.Surface((screen_width, screen_height), 0, 32)
    frame_marker.set_alpha(50)

    L = screen_width/2 - 100, screen_height/2
    R = screen_width/2 + 100, screen_height/2
    Rs = None
    Ls = None
    menupage = Menu(frame_surface, screen_width, screen_height)
    playGame = False
    simulate = False

    game = Game(screen_width, screen_height, scale, screen, frame_surface, frame_marker, clock, kinect)
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.unicode == "F" or event.unicode == "f":
                    # Change to fullscreen
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((screen_width*scale, screen_height*scale),
                                            pygame.HWSURFACE | pygame.DOUBLEBUF, 32)
                    else:
                        pygame.display.set_mode((screen_width*scale, screen_height*scale),
                                            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN, 32)
        
        kinectTracker = trackKinect(kinect)
        
        if kinectTracker != None:
            L, R, Ls, Rs = kinectTracker 

        else:
            mousePos = pygame.mouse.get_pos()
            Rx, Ry = mousePos[0], mousePos[1]
            R = Rx, Ry
            Rs = 3 
            L = Rx, Ry
            Ls = 3

        if playGame: 
            if simulate:
                game.runGame(True)
            else:
                game.runGame(False)
                    
        else:
            if Rs != None or Ls != None:
                if (menupage.checkHand((L, Ls), (R, Rs), screen_width/2, screen_height/2 - 150)):
                    playGame = True
                elif (menupage.checkHand((L, Ls), (R, Rs), screen_width/2, screen_height/2 + 150)):
                    playGame = True
                    simulate = True
        

                    
            # Update Background
            frame_surface.fill((0,0,0))
            frame_marker.fill((0,0,0))
   
            menupage.drawMenu((L, Ls), (R, Rs)) 
                
            drawKinect(frame_marker, L, R)
            
            h_to_w = float(frame_surface.get_height()) / frame_surface.get_width()
            target_height = int(h_to_w * screen.get_width())
            boidSurface = pygame.transform.scale(frame_surface,
                                                        (screen.get_width(), target_height))
            kinectSurface = pygame.transform.scale(frame_marker,
                                                        (screen.get_width(), target_height))
                                                            
            screen.blit(boidSurface, (0,0))
            screen.blit(kinectSurface, (0,0))
            
            surface_to_draw = None
            # print(clock.get_fps())
            pygame.display.update()
            clock.tick(120)
            
    kinect.close()    
    pygame.quit()    
        

    
# The code structure of the kinect is from the kinect workshop
class Game(object):

    def __init__(self, width, height, scale, screen, surface1, surface2, clock, kinect):
        self.done = False
        self.screen_width = width
        self.screen_height = height 
        self.scale = scale
        self.screen = screen
        self.clock = clock
        self.kinect = kinect
        self.bodies = None
        self.frame_surface = surface1
        self.frame_marker = surface2
        self.frame_marker.set_alpha(100)
        self.cur_right = 0, 0
        self.cur_left = 0, 0
        self.left_State = None
        self.right_State = None 
        self.count = 0
        self.countLeft = 0
        self.countRight = 0
        self.textsurface1 = None
        self.textsurface2 = None
        self.textsurface3 = None
        self.randomState = False
        self.simulateState = False
        self.randomColor = False
        self.goldren_ratio = 0.619033988749895

    def checkHand(self, X, Y, surface):

        sec = 10
        if self.left_State == 3:
            if self.checkOverlay(self.cur_left, X, Y, surface):
                self.countLeft +=1
        else:
            self.countLeft = 0
        
        if self.right_State == 3:
            if self.checkOverlay(self.cur_right, X, Y, surface):
                self.countRight +=1
        else:
            self.countRight = 0

        if self.countLeft >= sec or self.countRight >= sec:
            self.countLeft = 0
            self.countRight = 0
            return True

        else: return False

    def checkOverlay(self, Hand, X, Y, surface):

        if (X <= Hand[0] <= X + surface.get_width() and
            Y <= Hand[1] <= Y + surface.get_height()):
                return True
        return False

    def textDraw(self, DISPLAY1, DISPLAY2):
        myfont = pygame.font.SysFont('Century Gothic', 40)

        if (self.randomState):
            colors1 = (255, 255, 255)
        else:
            colors1 = (50, 50, 50)

        if (self.simulateState):
            colors2 = (255, 255, 255)
        else:
            colors2 = (50, 50, 50)

        # if (self.randomColor):
        hue = (random.random() + self.goldren_ratio) % 1
        colors3 = colorsys.hsv_to_rgb(hue, 0.7, 0.95)
        colors3 = colors3[0]*255, colors3[1]*255, colors3[2]*255

        self.textsurface1 = myfont.render("Random", True, colors1)
        self.textsurface2 = myfont.render("Simulate", True, colors2)
        self.textsurface3 = myfont.render("Random Color", True, colors3)

        if (self.checkOverlay(self.cur_left, 40, 40 + (70*4), self.textsurface1) or 
           self.checkOverlay(self.cur_right, 40, 40 + (70*4), self.textsurface1)):
            colors1 = (255, 0, 0)
            self.textsurface1 = myfont.render("Random", True, colors1)
            self.drawSelectionLoader(DISPLAY2)

        if (self.checkOverlay(self.cur_left, 40, 40 + (70*5), self.textsurface2) or 
           self.checkOverlay(self.cur_right, 40, 40 + (70*5), self.textsurface2)):
            colors2 = (255, 0, 0)
            self.textsurface2 = myfont.render("Simulate", True, colors2)
            self.drawSelectionLoader(DISPLAY2)

        if (self.checkOverlay(self.cur_left, 40, 40 + (70*6), self.textsurface3) or 
           self.checkOverlay(self.cur_right, 40, 40 + (70*6), self.textsurface3)):
            colors3 = (255, 0, 0)
            self.textsurface3 = myfont.render("Random Color", True, colors3)
            self.drawSelectionLoader(DISPLAY2)

        DISPLAY1.blit(self.textsurface1, (40, 40 + (70*4)))
        DISPLAY1.blit(self.textsurface2, (40, 40 + (70*5)))
        DISPLAY1.blit(self.textsurface3, (40, 40 + (70*6)))

    def drawSelectionLoader(self, DISPLAY):

        if self.left_State == 3:
            rect_left = self.cur_left[0], self.cur_left[1], 100, 100
            pygame.draw.arc(DISPLAY, (255,0,255), rect_left, 
                        math.pi/4, math.pi*2*(self.countLeft/10)+math.pi/4, 10)
        elif self.right_State == 3:
            rect_right = self.cur_right[0], self.cur_right[1], 100, 100
            pygame.draw.arc(DISPLAY, (255,0,0), rect_right, 
                        math.pi/4, math.pi*2*(self.countRight/10)+math.pi/4, 10)

    def stateChange(self, boidSystems):
        if self.right_State != None or self.left_State != None:
            
            # Random State
            if self.textsurface1 != None:
                if self.checkHand(40, 40 + (70*4), self.textsurface1):
                    if self.randomState:
                        self.randomState = False
                    else:
                        self.randomState = True
            if self.textsurface2 != None:
                if self.checkHand(40, 40 + (70*5), self.textsurface2):
                    if self.simulateState:
                        self.simulateState = False
                    else:
                        self.simulateState = True
            if self.textsurface3 != None:
                if self.checkHand(40, 40 + (70*6), self.textsurface3):
                    if self.randomColor:
                        self.randomColor = False
                    else:
                        self.randomColor = True
            
            
            if boidSystems[0].textsurface0 != None:
                # Alignment state
                if self.checkHand(40, 40, boidSystems[0].textsurface0):
    
                    for i in range(len(boidSystems)):
                        if boidSystems[i].controller[0]:
                            boidSystems[i].controller[0] = False
                            boidSystems[i].stateChange()
                        else:
                            boidSystems[i].controller[0] = True
                            boidSystems[i].stateChange()
                        
                # Cohesion state
                elif self.checkHand(40, 40 + (70*1), boidSystems[0].textsurface1):

                    for i in range(len(boidSystems)):
                        if boidSystems[i].controller[1]:
                            boidSystems[i].controller[1] = False
                            boidSystems[i].stateChange()
                        else:
                            boidSystems[i].controller[1] = True
                            boidSystems[i].stateChange()
            
                # Separation state
                elif self.checkHand(40, 40 + (70*2), boidSystems[0].textsurface2):
  
                    for i in range(len(boidSystems)):
                        
                        if boidSystems[i].controller[2]:
                            boidSystems[i].controller[2] = False
                            boidSystems[i].stateChange()
                        else:
                            boidSystems[i].controller[2] = True
                            boidSystems[i].stateChange()

                # Noise State
                elif self.checkHand(40, 40 + (70*3), boidSystems[0].textsurface3):

                    for i in range(len(boidSystems)):
                        
                        if boidSystems[i].controller[3]:
                            boidSystems[i].controller[3] = False
                            boidSystems[i].stateChange()
                        else:
                            boidSystems[i].controller[3] = True
                            boidSystems[i].stateChange()

                elif self.checkHand(1650, 40 + (70*4), boidSystems[0].textsurface8):
                    if boidSystems[0].controller[4] == 1:
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 2
                    elif boidSystems[0].controller[4] == 2:
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 1
                    elif boidSystems[0].controller[4] == 3:
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 4
                    elif boidSystems[0].controller[4] == 4:
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 3
                    elif boidSystems[0].controller[4] == 5:
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 6
                    elif boidSystems[0].controller[4] == 6:
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 5

                if boidSystems[0].controller[4] != 1:
                    if self.checkHand(1650, 40, boidSystems[0].textsurface4):
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 1

                if boidSystems[0].controller[4] != 3:
                    if self.checkHand(1650, 40 + (70*1), boidSystems[0].textsurface5):
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 3

                if boidSystems[0].controller[4] != 5:
                    if self.checkHand(1650, 40 + (70*2), boidSystems[0].textsurface6):
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 5

                if boidSystems[0].controller[4] != 7:
                    if self.checkHand(1650, 40 + (70*3), boidSystems[0].textsurface7):
                        for i in range(len(boidSystems)):
                            boidSystems[i].controller[4] = 7







    def runGame(self, simulateState):
        # list of boids
        boidSystems = []

        # generate and create boids
        for i in range(2):
            num1 = random.randint(20, 40)
            scale1 = 30 / num1
            newBoidSystem = Boids(num1, scale1, self.screen_width, self.screen_height)
            newBoidSystem.makeBoid()
            boidSystems.append(newBoidSystem)
    

        obstacles = Obstacles()
                               
        self.simulateState = simulateState

        count = 0
        self.frame_surface.fill((0,0,0))
        self.frame_marker.fill((0,0,0))
        
        #game loop
        while not self.done:
            # handle user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    # create an array of boids
                    num2 = random.randint(20, 40)
                    scale2 = 30 / num1
                    controller = copy.deepcopy(boidSystems[0].controller)
                    newBoidSystem = Boids(
                        num2, scale2, self.screen_width, self.screen_height, controller)
                    newBoidSystem.makeBoid()
                    boidSystems.append(newBoidSystem)
                    if len(boidSystems) > 5:
                        boidSystems.pop(0)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # create single boid
                    mousePos = pygame.mouse.get_pos()
                    mouseVec1 = pygame.math.Vector2((mousePos))
                    for i in range(len(boidSystems)):
                        boidSystems[i].addBoid(mouseVec1)

                elif event.type == pygame.KEYDOWN:

                    if event.unicode == "A" or event.unicode == "a":
                        for i in range(len(boidSystems)):
                            # Alignment state
                            if boidSystems[i].controller[0] == True:
                                boidSystems[i].controller[0] = False
                                boidSystems[i].stateChange()
                            else:
                                boidSystems[i].controller[0] = True
                                boidSystems[i].stateChange()

                    elif event.unicode == "C" or event.unicode == "c":
                        for i in range(len(boidSystems)):
                            # Cohesion state
                            if boidSystems[i].controller[1] == True:
                                boidSystems[i].controller[1] = False
                                boidSystems[i].stateChange()
                            else:
                                boidSystems[i].controller[1] = True
                                boidSystems[i].stateChange()

                    elif event.unicode == "S" or event.unicode == "s":
                        for i in range(len(boidSystems)):
                            # Seperation state
                            if boidSystems[i].controller[2] == True:
                                boidSystems[i].controller[2] = False
                                boidSystems[i].stateChange()
                            else:
                                boidSystems[i].controller[2] = True
                                boidSystems[i].stateChange()


                    elif event.unicode == "N" or event.unicode == "n":
                        for i in range(len(boidSystems)):
                            # Noise State
                            if boidSystems[i].controller[3] == True:
                                boidSystems[i].controller[3] = False
                                boidSystems[i].stateChange()
                            else:
                                boidSystems[i].controller[3] = True
                                boidSystems[i].stateChange()

                    elif event.unicode == "B" or event.unicode == "b":
                        for i in range(len(boidSystems)):
                            # Debug State
                            if boidSystems[i].controller[5] == True:
                                boidSystems[i].controller[5] = False
                                boidSystems[i].stateChange()
                            else:
                                boidSystems[i].controller[5] = True
                                boidSystems[i].stateChange()

                    elif event.unicode == "F" or event.unicode == "f":
                        # Change to fullscreen
                        if self.screen.get_flags() & pygame.FULLSCREEN:
                            pygame.display.set_mode((self.screen_width*self.scale, self.screen_height*self.scale),
                            pygame.HWSURFACE | pygame.DOUBLEBUF, 32)
                        else:
                            pygame.display.set_mode((self.screen_width*self.scale, self.screen_height*self.scale),
                                              pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN, 32)

                    elif event.unicode == "R" or event.unicode == "r":
                        # Random State
                        if self.randomState == True:
                            self.randomState = False
                        else:
                            self.randomState = True

                    elif event.unicode == "D" or event.unicode == "d":
                        # Draw State
                        if self.simulateState == True:
                            self.simulateState = False
                        else:
                           self.simulateState = True

                    elif event.unicode == "W" or event.unicode == "w":
                        # Make wall
                        mousePos = pygame.mouse.get_pos()
                        mouseVec2 = pygame.math.Vector2((mousePos))
                        obstaclesRadius = random.randint(10, 20)
                        obstacles.makeObstacles(mouseVec2, obstaclesRadius)

                    # Drawing Styles
                    elif event.unicode == "1":
                        for i in range(len(boidSystems)):
                            # Triangle State
                            boidSystems[i].controller[4] = 1

                    elif event.unicode == "2":
                        for i in range(len(boidSystems)):
                            # Arrow Trails State
                            boidSystems[i].controller[4] = 2

                    elif event.unicode == "3":
                        for i in range(len(boidSystems)):
                            # Circle State
                            boidSystems[i].controller[4] = 3

                    elif event.unicode == "4":
                        for i in range(len(boidSystems)):
                            # Trails State
                            boidSystems[i].controller[4] = 4

                    elif event.unicode == "5":
                        for i in range(len(boidSystems)):
                            # Diamond State
                            boidSystems[i].controller[4] = 5

                    elif event.unicode == "6":
                        for i in range(len(boidSystems)):
                            # Diamond Trail State
                            boidSystems[i].controller[4] = 6

                    elif event.unicode == "7":
                        for i in range(len(boidSystems)):
                            # Paper Trail State
                            boidSystems[i].controller[4] = 7

            kinectTracker = trackKinect(self.kinect)
            if kinectTracker != None:
                self.cur_left, self.cur_right, self.left_State, self.right_State = kinectTracker

            else:
                mousePos = pygame.mouse.get_pos()
                Rx, Ry = mousePos[0], mousePos[1]
                self.cur_right = Rx, Ry
                self.right_State = 3 
                self.cur_left = Rx, Ry
                self.left_State = 3

            self.stateChange(boidSystems)                             
                                           
            if self.randomState == False:
                #mousePos = pygame.mouse.get_pos()
                #Rx, Ry = mousePos[0], mousePos[1]
                Rx = (self.cur_right[0])
                Ry = (self.cur_right[1])
                Lx = (self.cur_left[0])
                Ly = (self.cur_left[1])
                
                target1 = pygame.math.Vector2((Rx, Ry))
                target2 = pygame.math.Vector2((Lx, Ly))
            else:
                if count % 30 == 0:
                    target1 = pygame.math.Vector2(
                        (random.random() * self.screen_width, random.random() * self.screen_height))
                    target2 = pygame.math.Vector2(
                        (random.random() * self.screen_width, random.random() * self.screen_height))
            count += 1

            if self.randomColor == True:
                for i in range(len(boidSystems)):
                    boidSystems[i].randomColor()
                self.randomColor = False
            # else:
            #     self.colorCount += 1
            #     if self.colorCount == 1:
            #         for i in range(len(boidSystems)):
            #             tempNum = boidSystems[i].num
            #             tempScale = boidSystems[i].scale
            #             controller = copy.deepcopy(boidSystems[0].controller)
            #             newBoidSystem = Boids(
            #                 tempNum, tempScale, self.screen_width, self.screen_height, controller)
            #             newBoidSystem.makeBoid()
            #             boidSystems.append(newBoidSystem)
            #             boidSystems.pop(0)
                
            for i in range(len(boidSystems)):
                if i % 2 == 0:
                    boidSystems[i].update(target1, target2, obstacles.obstaclesList)
                else:
                    boidSystems[i].update(target2, target1, obstacles.obstaclesList)

            # reset and draw things to screen
            if self.simulateState:
                # drawing mode off (keep filling the background)
                self.frame_surface.fill((0,0,0))

            self.frame_marker.fill((0,0,0))
            
            

            for i in range(len(boidSystems)):
                boidSystems[i].draw(self.frame_surface, self.frame_marker, False, 
                                    (self.cur_left, self.cur_right), (self.left_State, self.right_State),
                                    self.countLeft, self.countRight)

            self.textDraw(self.frame_surface, self.frame_marker)
            obstacles.drawObstacles(self.frame_surface)
            
            # Kinect hand tracking circles
            drawKinect(self.frame_marker, self.cur_left, self.cur_right)

            # resize the drawing to fit the screen.
            h_to_w = float(self.frame_surface.get_height()) / self.frame_surface.get_width()
            target_height = int(h_to_w * self.screen.get_width())
            boidSurface = pygame.transform.scale(self.frame_surface,
                                                     (self.screen.get_width(), target_height))
            kinectSurface = pygame.transform.scale(self.frame_marker,
                                                     (self.screen.get_width(), target_height))
            # Draw boid layer
            self.screen.blit(boidSurface, (0,0))
            # Draw kinect layer
            self.screen.blit(kinectSurface, (0,0))
            
            pygame.display.update()
            # print(self.clock.get_fps())
            self.clock.tick(120)

            
        self.kinect.close()    
        pygame.quit() 

run()



