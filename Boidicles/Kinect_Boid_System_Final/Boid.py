
import pygame
import numpy
import random
import copy
import sys

# Boid system from https://www.red3d.com/cwr/boids/ and http://www.kfish.org/boids/pseudocode.html

class Boid():

    def __init__(self, pos, maxSpeed, maxForce, scale, controller, width, height, color):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(
            (random.uniform(-maxSpeed, maxSpeed), random.uniform(-maxSpeed, maxSpeed)))
        self.accel = pygame.math.Vector2((0, 0))
        self.maxSpeed = maxSpeed
        self.maxForce = maxForce
        self.target = None
        self.allPos = []
        self.allVel = []
        self.friends = set()
        self.scale = scale
        self.width = width
        self.height = height
        self.controller = controller
        self.color = color

    def __hash__(self):
        return hash((int(self.pos[0]), int(self.pos[1])))

    def limit(self, vector1, maxVal):
        length = pygame.math.Vector2.length(vector1)

        if length <= maxVal:
            return vector1
        else:
            normalizeTemp = pygame.math.Vector2.normalize(vector1)
            return normalizeTemp * maxVal

    def update(self, width, height):
        self.velocity += self.accel
        self.velocity = self.limit(self.velocity, self.maxSpeed)

        # Only store data when trail mode is activated
        if self.controller[4] == 2 or self.controller[4] == 4 or self.controller[4] == 6 or self.controller[4] == 7:
            vel = int(self.velocity[0]), int(self.velocity[1])
            self.allVel.append(vel)

            if len(self.allVel) > 10:
                self.allVel.pop(0)

            pos = int(self.pos[0]), int(self.pos[1])
            self.allPos.append(pos)

            if len(self.allPos) > 10:
                self.allPos.pop(0)
        else:
            self.allPos.clear()
            self.allVel.clear()

        self.pos += self.velocity

        if self.pos[0] > width:
            self.pos[0] = 0
            self.allPos.clear()
            self.allVel.clear()
        elif self.pos[0] < 0:
            self.pos[0] = width
            self.allPos.clear()
            self.allVel.clear()
        if self.pos[1] > height:
            self.pos[1] = 0
            self.allPos.clear()
            self.allVel.clear()
        elif self.pos[1] < 0:
            self.pos[1] = height
            self.allPos.clear()
            self.allVel.clear()

        self.accel *= 0

    def applyForce(self, force):
        self.accel += force

    def seek(self, target):
        # Seek the target (Move to target/attractor point)
        self.target = target
        distance = target - self.pos
        desiredVec = pygame.math.Vector2.normalize(distance)
        desiredVec *= self.maxSpeed

        steer = desiredVec - self.velocity
        steer = self.limit(steer, self.maxForce)

        return steer

    def arrive(self, target):
        self.target = target
        distance = target - self.pos
        if pygame.math.Vector2.length(distance) != 0:
            desiredVec = pygame.math.Vector2.normalize(distance)
            distanceLength = pygame.math.Vector2.length(distance)

            if distanceLength < 100:
                m = (distanceLength / 100) * self.maxSpeed
                desiredVec *= m
            else:
                desiredVec *= self.maxSpeed

            steer = (desiredVec - self.velocity)
            steer = self.limit(steer, self.maxForce)

            return steer
        else:
            return pygame.math.Vector2(0, 0)

    def separate(self, boids):
        count = 0
        steer = pygame.math.Vector2(0, 0)
        separation = 100 * self.scale

        angle1 = self.pos.angle_to(self.velocity)

        for i in range(len(boids)):
            if self.pos != boids[i].pos:
                diff = self.pos - boids[i].pos
                distance = pygame.math.Vector2.length(diff)
                angle2 = self.pos.angle_to(diff)

                if 0 < distance < separation and -60 < angle2-angle1 < 60:
                    diff = self.pos - boids[i].pos
                    diff = pygame.math.Vector2.normalize(diff)
                    steer += diff
                    count += 1

        if count > 0:
            steer /= count

        steerLength = pygame.math.Vector2.length(steer)
        if steerLength > 0:
            steer = pygame.math.Vector2.normalize(steer)
            steer *= self.maxSpeed

            steer -= self.velocity
            steer = self.limit(steer, self.maxForce)

            return steer
        else:
            return pygame.math.Vector2(0, 0)

    def cohesion(self, boids):
        count = 0
        addSum = pygame.math.Vector2(0, 0)
        cohesion = 60 * self.scale

        angle1 = self.pos.angle_to(self.velocity)

        for i in range(len(boids)):
            if self.pos != boids[i].pos:
                diff = self.pos - boids[i].pos
                distance = pygame.math.Vector2.length(diff)
                angle2 = self.pos.angle_to(diff)

                if 0 < distance < cohesion and -60 < angle2-angle1 < 60:
                    addSum += boids[i].pos
                    count += 1

        if count > 1:
            addSum /= count
            addSum -= self.pos
            addSum = pygame.math.Vector2.normalize(addSum)

            return self.seek(addSum)
        else:
            return pygame.math.Vector2(0, 0)

    def align(self, boids):
        addSum = pygame.math.Vector2(0, 0)
        align = 60 * self.scale / 1.3
        count = 0

        angle1 = self.pos.angle_to(self.velocity)

        for i in range(len(boids)):
            if self.pos != boids[i].pos:
                diff = self.pos - boids[i].pos
                distance = pygame.math.Vector2.length(diff)
                angle2 = self.pos.angle_to(diff)

                if 0 < distance < align and -60 < angle2-angle1 < 60:
                    if pygame.math.Vector2.length(boids[i].pos) != 0:
                        # copyboid = boids[i].pos
                        # copyboid = pygame.math.Vector2.normalize(copyboid)
                        # copyboid /= distance
                        # addSum += copyboid
                        addSum += pygame.math.Vector2(boids[i].velocity)
                        count += 1

        if count > 0:
            addSum /= count
            addSum = pygame.math.Vector2.normalize(addSum)
            addSum *= self.maxSpeed
            steer = addSum - self.velocity
            steer = self.limit(steer, self.maxForce)

            return steer
        else:
            return pygame.math.Vector2(0, 0)

    def getAverageColor(self):
        count = 0
        neighbor = 50
        R, G, B = 0, 0, 0
        for boid in self.friends:
            R += boid.color[0]
            G += boid.color[1]
            B += boid.color[2]

        if len(self.friends) > 0:
            R /= len(self.friends)
            G /= len(self.friends)
            B /= len(self.friends)

            self.color = (R, G, B)

    def getFriends(self, boids):

        friendRadius = 60 * self.scale

        for i in range(len(boids)):
            if self.pos != boids[i].pos:
                diff = self.pos - boids[i].pos
                distance, angle = pygame.math.Vector2.as_polar(diff)

                if 0 < distance < friendRadius:
                    self.friends.add(boids[i])
                else:
                    self.friends.discard(boids[i])

    def collision(self, obstacles):
        boidRadius = 60 * self.scale
        steer = pygame.math.Vector2(0, 0)
        for i in range(len(obstacles)):
            pos, obstacleRadius = obstacles[i]

            diff = self.pos - pos
            distance, angle = pygame.math.Vector2.as_polar(diff)

            if 0 < distance < obstacleRadius + boidRadius:
                diff = pygame.math.Vector2.normalize(diff)
                diff /= distance
                steer += diff

        steerLength = pygame.math.Vector2.length(steer)
        if steerLength > 0:
            steer = pygame.math.Vector2.normalize(steer)
            steer *= self.maxSpeed
            steer -= self.velocity
            steer = self.limit(steer, self.maxForce)
            return steer

        else:
            return pygame.math.Vector2(0, 0)

    def avoid(self, target):
        distance = target - self.pos
        if pygame.math.Vector2.length(distance) != 0:
            desiredVec = pygame.math.Vector2.normalize(distance)
            distanceLength = pygame.math.Vector2.length(distance)

            if distanceLength < 100:
                m = (distanceLength / 100) * self.maxSpeed
                desiredVec *= m
            else:
                desiredVec *= self.maxSpeed

            steer = (desiredVec - self.velocity)
            steer = -self.limit(steer, self.maxForce)

            return steer
        else:
            return pygame.math.Vector2(0, 0)

    def applyBehaviors(self, boids, target1, target2, obstacles):
        # apply all behavior with certain scalar value 
        # self.getFriends(boids)
        # self.getAverageColor()

        # Collision detection for wall
        if len(obstacles) > 0:
            collision = self.collision(obstacles)
            collision *= 3
            self.applyForce(collision)

        # Alignment Behavior
        if (self.controller[0]):
            align = self.align(boids)
            align *= 1
            self.applyForce(align)

        # Cohesion Behavior
        if (self.controller[1]):
            cohesion = self.cohesion(boids)
            cohesion *= 0.5
            self.applyForce(cohesion)

        # Move to Attractor
        if target1 != None:
            arrive = self.arrive(target1)
            arrive *= 1
            self.applyForce(arrive)

        # small Noise
        if (self.controller[3]):
            noise = random.uniform(-1, 1), random.uniform(-1, 1)
            noise = pygame.math.Vector2(noise)
            noise *= 0.01
            self.applyForce(noise)

        # Seperate Behavior
        if (self.controller[2]):
            separate = self.separate(boids)
            separate *= 2
            self.applyForce(separate)
    
    def drawArrow(self, DISPLAY, scale):
        # Draw Arrow
        distance = self.velocity
        degree = pygame.math.Vector2.as_polar(distance)[1] - 180

        pt1 = int(self.pos[0]), int(self.pos[1])
        pt2 = int(self.pos[0] + (20 * scale)
                  ), int(self.pos[1] - (5 * scale))
        pt3 = int(self.pos[0] + (20 * scale)
                  ), int(self.pos[1] + (5 * scale))
        pt4 = int(self.pos[0] - (20 * scale)), int(self.pos[1])

        vecPt1 = pygame.math.Vector2(pt1)
        vecPt2 = pygame.math.Vector2(pt2)
        vecPt3 = pygame.math.Vector2(pt3)
        vecPt4 = pygame.math.Vector2(pt4)
        tempPt2 = vecPt2 - vecPt1
        tempPt3 = vecPt3 - vecPt1
        tempPt4 = vecPt4 - vecPt1

        pt2 = pygame.math.Vector2.rotate(tempPt2, degree) + vecPt1
        pt3 = pygame.math.Vector2.rotate(tempPt3, degree) + vecPt1
        pt4 = pygame.math.Vector2.rotate(tempPt4, degree) + vecPt1
        points = [pt1, pt2, pt3]
        pygame.draw.polygon(DISPLAY, self.color, points)
        # points2 = [(int(pt1[0]), int(pt1[1])),
        #            (int(pt4[0]), int(pt4[1]))]
        # pygame.draw.aalines(DISPLAY, (255, 0, 0), False, points2, 2)

    def drawArrowTrails(self, DISPLAY, scale):
        # Draw all arrows
        for i in range(len(self.allVel)):
            distance = pygame.math.Vector2(self.allVel[i])
            degree = pygame.math.Vector2.as_polar(distance)[1] - 180

            pt1 = int(self.allPos[i][0]), int(self.allPos[i][1])
            pt2 = int(self.allPos[i][0] + (20 * scale)
                      ), int(self.allPos[i][1] - (5 * scale))
            pt3 = int(self.allPos[i][0] + (20 * scale)
                      ), int(self.allPos[i][1] + (5 * scale))
            pt4 = int(self.allPos[i][0] - (20 * scale)
                      ), int(self.allPos[i][1])

            vecPt1 = pygame.math.Vector2(pt1)
            vecPt2 = pygame.math.Vector2(pt2)
            vecPt3 = pygame.math.Vector2(pt3)
            vecPt4 = pygame.math.Vector2(pt4)
            tempPt2 = vecPt2 - vecPt1
            tempPt3 = vecPt3 - vecPt1
            tempPt4 = vecPt4 - vecPt1

            pt2 = pygame.math.Vector2.rotate(tempPt2, degree) + vecPt1
            pt3 = pygame.math.Vector2.rotate(tempPt3, degree) + vecPt1
            pt4 = pygame.math.Vector2.rotate(tempPt4, degree) + vecPt1
            points = [pt1, pt2, pt3]

            R, G, B = self.color
            R -= (10 * (len(self.allVel) - i))
            G -= (10 * (len(self.allVel) - i))
            B -= (10 * (len(self.allVel) - i))
            if R < 0:
                R = 0
            if G < 0:
                G = 0
            if B < 0:
                B = 0

            pygame.draw.polygon(DISPLAY, (R, G, B), points)
            # pygame.draw.aalines(DISPLAY, (255, 0, 0), False, [pt1, pt4], 2)

    def drawCircleTrails(self, DISPLAY, scale, radius):

        for i in range(len(self.allPos)):
            pt1 = int(self.allPos[i][0]), int(self.allPos[i][1])
            R, G, B = self.color
            R -= (10 * (len(self.allPos) - i))
            G -= (10 * (len(self.allPos) - i))
            B -= (10 * (len(self.allPos) - i))
            if R < 0:
                R = 0
            if G < 0:
                G = 0
            if B < 0:
                B = 0

            newRadius = radius - (0.25 * (len(self.allPos) - i))
            pygame.draw.circle(DISPLAY, (R, G, B), pt1, int(newRadius), 0)

    def drawDiamond(self, DISPLAY, scale):
        distance = self.velocity
        degree = pygame.math.Vector2.as_polar(distance)[1] - 180

        pt1 = int(self.pos[0]), int(self.pos[1])
        pt2 = int(self.pos[0] + (20 * scale)
                  ), int(self.pos[1] - (5 * scale))
        pt3 = int(self.pos[0] + (20 * scale)
                  ), int(self.pos[1] + (5 * scale))
        pt4 = int(self.pos[0] + (40 * scale)), int(self.pos[1])

        vecPt1 = pygame.math.Vector2(pt1)
        vecPt2 = pygame.math.Vector2(pt2)
        vecPt3 = pygame.math.Vector2(pt3)
        vecPt4 = pygame.math.Vector2(pt4)
        tempPt2 = vecPt2 - vecPt1
        tempPt3 = vecPt3 - vecPt1
        tempPt4 = vecPt4 - vecPt1

        pt2 = pygame.math.Vector2.rotate(tempPt2, degree) + vecPt1
        pt3 = pygame.math.Vector2.rotate(tempPt3, degree) + vecPt1
        pt4 = pygame.math.Vector2.rotate(tempPt4, degree) + vecPt1
        points = [pt1, pt2, pt4, pt3]
        pygame.draw.polygon(DISPLAY, self.color, points)

    def drawDiamondTrails(self, DISPLAY, scale):
        for i in range(len(self.allVel)):
            distance = pygame.math.Vector2(self.allVel[i])
            degree = pygame.math.Vector2.as_polar(distance)[1] - 180

            pt1 = int(self.allPos[i][0]), int(self.allPos[i][1])
            pt2 = int(self.allPos[i][0] + (20 * scale)
                      ), int(self.allPos[i][1] - (5 * scale))
            pt3 = int(self.allPos[i][0] + (20 * scale)
                      ), int(self.allPos[i][1] + (5 * scale))
            pt4 = int(self.allPos[i][0] + (40 * scale)
                      ), int(self.allPos[i][1])

            vecPt1 = pygame.math.Vector2(pt1)
            vecPt2 = pygame.math.Vector2(pt2)
            vecPt3 = pygame.math.Vector2(pt3)
            vecPt4 = pygame.math.Vector2(pt4)
            tempPt2 = vecPt2 - vecPt1
            tempPt3 = vecPt3 - vecPt1
            tempPt4 = vecPt4 - vecPt1

            pt2 = pygame.math.Vector2.rotate(tempPt2, degree) + vecPt1
            pt3 = pygame.math.Vector2.rotate(tempPt3, degree) + vecPt1
            pt4 = pygame.math.Vector2.rotate(tempPt4, degree) + vecPt1
            points = [pt1, pt2, pt4, pt3]

            R, G, B = self.color
            R -= (10 * (len(self.allVel) - i))
            G -= (10 * (len(self.allVel) - i))
            B -= (10 * (len(self.allVel) - i))
            if R < 0:
                R = 0
            if G < 0:
                G = 0
            if B < 0:
                B = 0

            pygame.draw.polygon(DISPLAY, (R, G, B), points)

    def drawLineTrails(self, DISPLAY, thickness):
        pts = []
        for i in range(len(self.allPos)):
            pts.append(self.allPos[i])
        if len(pts) > 2:
            pygame.draw.lines(DISPLAY, self.color,
                              False, pts, int(thickness))

    def drawLineToAttractor(self, DISPLAY):
        if self.target != None:
            points = [(int(self.target[0]), int(self.target[1])),
                      (int(self.pos[0]), int(self.pos[1]))]
            pygame.draw.aalines(DISPLAY, (255, 255, 0), False, points, 2)

    def dynamicDraw(self, DISPLAY, boids, scale):

        thickness = 10 * scale
        radius = 10 * scale

        if self.controller[4] == 1:
            # Arrow
            self.drawArrow(DISPLAY, scale)

        elif self.controller[4] == 2:
            # Arrow Trails
            self.drawArrowTrails(DISPLAY, scale)

        elif self.controller[4] == 3:
            # Circles
            pygame.draw.circle(DISPLAY, self.color,
                               (int(self.pos[0]), int(self.pos[1])), int(radius), 0)

        elif self.controller[4] == 4:
            # Circles Trails
            self.drawCircleTrails(DISPLAY, scale, radius)

        elif self.controller[4] == 5:
            # Diamonds
            self.drawDiamond(DISPLAY, scale)

        if self.controller[4] == 6:
            # Diamond Trail
            self.drawDiamondTrails(DISPLAY, scale)

        elif self.controller[4] == 7:
            # Line Trails
            self.drawLineTrails(DISPLAY, thickness)

        if self.controller[5] == True:
            # Lines to Attractor Point
            self.drawLineToAttractor(DISPLAY)
            # Lines between Boids
            # for i in range(len(boids)):
            #     points = [self.pos, boids[i].pos]
            #     pygame.draw.aalines(DISPLAY, (255, 255, 0), False, points, 2)

