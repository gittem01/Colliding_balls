import cv2
import math
import numpy as np
import time
from random import randrange as rand

WIDTH = 1280
HEIGHT = 720
number = 20 # For better simulation - With less bugs

def cos_ofvectangle(vec1, vec2):
    mult = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    return mult / (((vec1[0]**2 + vec1[1]**2)**0.5) * ((vec2[0]**2 + vec2[1]**2)**0.5))


def projection(vec1, vec2):
    div = (vec1[0] * vec2[0] + vec1[1] * vec2[1]) / (vec2[0]**2 + vec2[1]**2)
    return (vec2[0] * div, vec2[1] * div)


def after_collision(obj1, obj2, img):
    # Finding relative velocities
    vec = (obj1.x - obj2.x, obj1.y - obj2.y)
    perpv = (-vec[1], vec[0])
    vecv1 = (obj1.vx, obj1.vy)
    vecv2 = (obj2.vx, obj2.vy)

    controlv = (vecv1[0] - vecv2[0], vecv1[1] - vecv2[1])
    #if (controlv[0] > 0 and vec[0] > 0) or (controlv[1] > 0 and vec[1] > 0):
    #    return
    #if (controlv[0] < 0 and vec[0] < 0) or (controlv[1] < 0 and vec[1] < 0):
    #    return

    uncv1 = projection(vecv1, perpv)
    uncv2 = projection(vecv2, perpv)
    chv1 = projection(vecv1, vec)
    chv2 = projection(vecv2, vec)

    sqcv1x = (chv1[0]*(obj1.mass-obj2.mass)+2*obj2.mass*chv2[0])/(obj1.mass + obj2.mass)
    sqcv1y = (chv1[1]*(obj1.mass-obj2.mass)+2*obj2.mass*chv2[1])/(obj1.mass + obj2.mass)
    sqcv2x = (chv2[0]*(obj2.mass-obj1.mass)+2*obj1.mass*chv1[0])/(obj1.mass + obj2.mass)
    sqcv2y = (chv2[1]*(obj2.mass-obj1.mass)+2*obj1.mass*chv1[1])/(obj1.mass + obj2.mass)
    chv1 = (sqcv1x, sqcv1y)
    chv2 = (sqcv2x, sqcv2y)

    obj1.vx = chv1[0] + uncv1[0]
    obj1.vy = chv1[1] + uncv1[1]
    obj2.vx = chv2[0] + uncv2[0]
    obj2.vy = chv2[1] + uncv2[1]
    while ((obj1.x - obj2.x) ** 2 + (obj1.y - obj2.y) ** 2)**0.5 < obj1.r + obj2.r:
        obj1.move(50);obj2.move(50)
    #cv2.arrowedLine(img, (round(obj1.x), round(obj1.y)), (round(obj1.x + chv1[0]*30), round(obj1.y + chv1[1]*15)), (0, 255, 0), 1)
    #cv2.arrowedLine(img, (round(obj2.x), round(obj2.y)), (round(obj2.x + chv2[0]*30), round(obj2.y + chv2[1]*15)), (0, 255, 0), 1)

def collision(lst, img):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if ((lst[i].x - lst[j].x)**2 + (lst[i].y - lst[j].y)**2)**0.5 < (lst[i].r + lst[j].r):
                after_collision(lst[i], lst[j], img)


class obj:
    def __init__(self, mass, vx, vy, x, y, r, color, id):
        self.mass = mass
        self.vx = vx
        self.vy = vy
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.id = id
    def move(self, number):
        self.x += self.vx/number
        self.y += self.vy/number


writer = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 60,(WIDTH, HEIGHT))

#objs = [obj(5, 1, 0, 100, 500, 20, (255, 0, 0)), obj(5, 0, 0, 500, 500, 20, (0, 255, 0))]
objs = [obj(500, 0, -40, 200, 400, 50, (255, 255, 255), 1)]
for i in range(30):
    objs.append(obj(rand(100, 500), 0, 0, WIDTH*i/100, HEIGHT*i/100, 5, (rand(255), rand(255), rand(255)), rand(9999999)))

for frame in range(2000):
    print(frame)
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    for i in range(number): # For fixing bugs
        collision(objs, img)
        for i in objs:
            cv2.circle(img, (round(i.x), round(i.y)), i.r, (0 ,255 - (i.mass*255)/500, (i.mass*255)/500), -1)
            i.move(number)
            if i.x + i.r > WIDTH:
                i.vx = abs(i.vx)*-1
            if i.r  > i.x:
                i.vx= abs(i.vx)
            if i.y + i.r > HEIGHT:
                i.vy = abs(i.vy) * -1
            if i.r > i.y:
                i.vy = abs(i.vy)
    writer.write(img.astype('uint8'))
    #cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

writer.release()
