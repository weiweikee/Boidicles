import pygame
import numpy
import random
import copy
import sys


class Path():
    def __init__(self, radius, width, height):
        self.points = []
        self.radius = radius
        self.width = width
        self.height = height

    def addPoint(self, x, y):
        self.points.append(pygame.math.Vector2(x, y))
    
    def flipY(self, y):
        return -y + self.height

    def draw(self, DISPLAY):
        for i in range(len(self.points)):
            self.points[i][1] = self.flipY(self.points[i][1])
            pygame.draw.aalines(DISPLAY, (100, 0, 0),
                                False, self.points)

    def generatePath(self):
        # Random path generation
        chances = random.randint(2, 10)
        section = self.width / (chances - 1)
        for i in range(chances):
            self.addPoint((i * section),
                          random.uniform(0, self.height))



