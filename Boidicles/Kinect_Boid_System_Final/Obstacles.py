import pygame
import numpy
import random
import copy
import sys


class Obstacles():
    def __init__(self):
        self.obstaclesList = []

    def makeObstacles(self, pos, r):
        pos = pygame.math.Vector2(pos)
        radius = r
        self.obstaclesList.append((pos, r))

    def drawObstacles(self, DISPLAY):

        for i in range(len(self.obstaclesList)):
            pos, r = self.obstaclesList[i]
            pygame.draw.circle(DISPLAY, (255, 0, 0),
                               (int(pos[0]), int(pos[1])), int(r), 0)
