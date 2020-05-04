import cv2
import numpy as np
import time
import math
import random
from random import randrange as rand
from pydub import AudioSegment
from pydub.playback import play
import os
import sys

WIDTH = 1600
HEIGHT = 900
FPS = 60
number = 100 # For better simulation // (+) With less bug and more accuracy BUT slower //

def projection(vec1, vec2):
    div = (vec1[0] * vec2[0] + vec1[1] * vec2[1]) / (vec2[0]**2 + vec2[1]**2)
    return (vec2[0] * div, vec2[1] * div)


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

    # Some vector operation
    # Source https://en.wikipedia.org/wiki/Elastic_collision

    sqcv1x = (chv1[0]*(obj1.mass-obj2.mass)+2*obj2.mass*chv2[0])/(obj1.mass + obj2.mass)
    sqcv1y = (chv1[1]*(obj1.mass-obj2.mass)+2*obj2.mass*chv2[1])/(obj1.mass + obj2.mass)
    sqcv2x = (chv2[0]*(obj2.mass-obj1.mass)+2*obj1.mass*chv1[0])/(obj1.mass + obj2.mass)
    sqcv2y = (chv2[1]*(obj2.mass-obj1.mass)+2*obj1.mass*chv1[1])/(obj1.mass + obj2.mass)
    chv1 = (sqcv1x, sqcv1y)
    chv2 = (sqcv2x, sqcv2y)

    obj1.vx = (chv1[0] + uncv1[0])
    obj1.vy = (chv1[1] + uncv1[1])
    obj2.vx = (chv2[0] + uncv2[0])
    obj2.vy = (chv2[1] + uncv2[1])

    #gives new position to nested objects (Only for one of them for now)
    angleBetween = math.atan2(obj2.y-obj1.y, obj2.x - obj1.x)
    obj2.x = math.cos(angleBetween)*(obj1.r + obj2.r) + obj1.x
    obj2.y = math.sin(angleBetween)*(obj1.r + obj2.r) + obj1.y

def collision(lst, img, sl, frame):
    global coll, number
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if ((lst[i].x - lst[j].x)**2 + (lst[i].y - lst[j].y)**2)**0.5 < (lst[i].r + lst[j].r):
                after_collision(lst[i], lst[j], img)
                coll += 1
                if (frame, i2) not in sl:
                    sl.append((frame, i2))

def gravity(objl):
    for i in objl:
        i.vy += 0.01

class obj: # May be improved
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
        self.x += self.vx/(number)
        self.y += self.vy/(number)


writer = cv2.VideoWriter("output_files/output_video.avi", cv2.VideoWriter_fourcc(*"MJPG"), FPS,(WIDTH, HEIGHT))

objs= []

objs.append(obj(10000, -2, 0, 500, 500, 10, (255, rand(255), rand(255)), "not_yet"))
objs.append(obj(1, -2, 0, 300, 500, 10, (255, rand(255), rand(255)), "not_yet"))

for i in range(1, 7):
    for j in range(i):
        objs.append(obj(10, 0, 0, i*150+150, j*150+30+(7-i)*10, 30, (255, rand(255), rand(255)), "not_yet"))

objs.append(obj(10, 2, -3, 500, 500, 10, (255, rand(255), rand(255)), "not_yet"))

sl = []
coll = 0
times = 1000


for frame in range(1000):

    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)

    for i2 in range(number): # For fixing bugs
        collision(objs, img, sl, frame)
        #gravity(objs)
        for i in objs:
            i.move(number)
            if i2 == number-1:

                #Visualization
                cv2.circle(img, (round(i.x), round(i.y)), i.r,
                (255, 255, 255), -1, lineType=cv2.LINE_AA)

                #cv2.arrowedLine(img, (round(i.x), round(i.y)), (round(i.x + i.vx*100),
                # round(i.y + i.vy*100)), (255, 0, 0), 3, line_type=cv2.LINE_AA)

                #Visulization
                cv2.circle(img, (round(i.x), round(i.y)), i.r,
                (255, 255, 255), -1, lineType=None)

                cv2.arrowedLine(img, (round(i.x), round(i.y)), (round(i.x + i.vx*100),
                 round(i.y + i.vy*100)), (255, 0, 0), 3, line_type=cv2.LINE_AA)

            if i.x + i.r >= WIDTH:
                i.vx = -i.vx
                coll += 1
                if (frame, i2) not in sl:
                    sl.append((frame, i2))
                while i.x + i.r > WIDTH:
                    i.move(times)
            if i.r  >= i.x:
                i.vx = abs(i.vx)
                coll += 1
                if (frame, i2) not in sl:
                    sl.append((frame, i2))

                while i.r  >= i.x:
                    i.move(times)
            if i.y + i.r >= HEIGHT:
                coll += 1
                i.vy = -i.vy
                if (frame, i2) not in sl:
                    sl.append((frame, i2))
                while i.y + i.r >= HEIGHT:
                    i.move(times)

            if i.r >= i.y:

                coll += 1
                i.vy = abs(i.vy)
                if (frame, i2) not in sl:
                    sl.append((frame, i2))
                while i.r >= i.y:
                    i.move(times)


    cv2.putText(img, str("Total Collision : " + str(coll)), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
    (255,255,255), 2)
    writer.write(img.astype('uint8'))
    cv2.imshow("img", img)
    if cv2.waitKey(1) == ord("q"):
        break

sound = AudioSegment.silent(duration=int(frame/FPS*1000))
audio = AudioSegment.from_wav("./sound_files/dup.wav")
counter = 0
print("\n")
for i in sl:
    print("%" + str(int(counter/len(sl)*100)), end = "\r")
    counter += 1
    sound = sound.overlay(audio, position=int((i[0]+(i[1]/number))/FPS*1000))

sound.export("output_files/output_sound.wav", format="wav")
# U need to install fmmpeg first
# For windows add ffmpeg to the PATH

os.system("ffmpeg -i output_files/output_video.avi -i output_files/output_sound.wav -c copy output_files/final_output.mkv -y")

writer.release()
