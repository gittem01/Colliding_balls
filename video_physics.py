import cv2
import math
import numpy as np
import time
from random import randrange as rand
from pydub import AudioSegment
from pydub.playback import play
import os

WIDTH = 1280
HEIGHT = 720
FPS = 60
number = 5000 # For better simulation (+) With less bugs (-)Slower

def projection(vec1, vec2):
    div = (vec1[0] * vec2[0] + vec1[1] * vec2[1]) / (vec2[0]**2 + vec2[1]**2)
    return (vec2[0] * div, vec2[1] * div)

def gravity(object_list, acceleration):
    for obj in object_list:
        obj.vy += acceleration/number

def after_collision(obj1, obj2, img):
    # Finding relative velocities
    vec = (obj1.x - obj2.x, obj1.y - obj2.y)
    perpv = (-vec[1], vec[0])
    vecv1 = (obj1.vx, obj1.vy)
    vecv2 = (obj2.vx, obj2.vy)

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

    #gives new position to nested objects
    while ((obj1.x - obj2.x) ** 2 + (obj1.y - obj2.y) ** 2)**0.5 < obj1.r + obj2.r:
        obj1.move(5000);obj2.move(5000)

    #Visulization
    #cv2.arrowedLine(img, (round(obj1.x), round(obj1.y)), (round(obj1.x + chv1[0]*30), round(obj1.y + chv1[1]*15)), (0, 255, 0), 1)
    #cv2.arrowedLine(img, (round(obj2.x), round(obj2.y)), (round(obj2.x + chv2[0]*30), round(obj2.y + chv2[1]*15)), (0, 255, 0), 1)

def collision(lst, img, sl, frame):
    global coll, number
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if ((lst[i].x - lst[j].x)**2 + (lst[i].y - lst[j].y)**2)**0.5 < (lst[i].r + lst[j].r):
                after_collision(lst[i], lst[j], img)
                coll += 1
                if (frame, number) not in sl:
                    sl.append((frame, i2))

class obj:
    def __init__(self, mass, vx, vy, x, y, r, color, audio):
        self.mass = mass
        self.vx = vx
        self.vy = vy
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.audio = audio
    def move(self, number):
        self.x += self.vx/number
        self.y += self.vy/number


writer = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), FPS,(WIDTH, HEIGHT))

objs = [obj(100000000, -0.5, 0, 600, 400, 50, (255, rand(255), rand(255)), "note.wav"),
        obj(1, 0, 0, 300, 400, 50, (255, rand(255), rand(255)), "note.wav")]

"""
for i in range(10):
    for j in range(10):
        objs.append(obj(10, rand(10), rand(10), i*50+50, j*50+50, 5, (255, rand(255), rand(255)), "note.wav"))
        print(i*50+50, j*50+50)
"""

sl = []
coll = 0

for frame in range(1500):
    print(frame)

    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)

    for i2 in range(number): # For fixing bugs
        collision(objs, img, sl, frame)
        #gravity(objs, 10)
        for i in objs:
            i.move(number)
            if i2 == number-1:
                cv2.circle(img, (round(i.x), round(i.y)), i.r, (255, 255, 255), -1)
                cv2.putText(img, "m = " + str(i.mass), (round(i.x), round(i.y)), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                (0, 0, 255), 1)
            if i.x + i.r > WIDTH:
                i.vx = abs(i.vx) * -1
                coll += 1
                while i.x + i.r > WIDTH:
                    i.move(500)
                if (frame, number) not in sl:
                    sl.append((frame, i2))
            if i.r  > i.x:
                coll += 1
                i.vx = abs(i.vx)
                while i.r  > i.x:
                    i.move(500)
                if (frame, number) not in sl:
                    sl.append((frame, i2))
            if i.y + i.r > HEIGHT:
                coll += 1
                i.vy = abs(i.vy) * -1
                while i.y + i.r > HEIGHT:
                    i.move(500)
                if (frame, number) not in sl:
                    sl.append((frame, i2))
            if i.r > i.y:
                coll += 1
                i.vy = abs(i.vy)
                while i.r > i.y:
                    i.move(500)
                if (frame, number) not in sl:
                    sl.append((frame, i2))
    cv2.putText(img, str("Total Collision : " + str(coll)), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
    (255,255,255), 2)
    writer.write(img.astype('uint8'))
    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
sound = AudioSegment.silent(duration=int(frame/FPS*1000))
audio = AudioSegment.from_wav("tick.wav")
for i in sl:
    sound = sound.overlay(audio, position=int((i[0]+(i[1]/number))/FPS*1000))

sound.export("output.wav", format="wav")
os.system("ffmpeg -i output.avi -i output.wav -c copy output.mkv")
writer.release()
