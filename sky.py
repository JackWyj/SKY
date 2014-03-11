# -*- coding: cp936 -*-
# Game Sky 1.0.0
# By JackWoo 2014-2-20

import sys
import random
import copy
import os
import math
import pygame
from pygame.locals import *



class Cloud():
    """
    this cloud is set fot the cloud in the sky, it is the decoration for the game
    """
    def __init__(self,img,rect,speed):
        #img is the surface of the pictures of clouds
        #rect is the position rectangle of the clouds
        #while flag is 0 the robot doesn't overlap the clouds,ortherwise 1 for overlap
        #as you can see, you well see variable in every class, 
        #it is functional that by every 6 ticks,the clouds update by themselves.
        self.img = img
        self.rect = rect
        self.flag = 0
        self.count = 1

    def update2(self,screen,r_android,dead):
        #while variable dead is 1, it means the robot has been dead, or 1 for alive
        if dead == 1:
            return -1
        #while the rect move outside the window's area, 
        #it should return a value for the control center to ignore them
        if self.rect.bottom < 0:
            return 1
        self.count += 1
        if self.count % 6 == 0:
            self.rect.top -= speed
            if self.rect.colliderect(r_android):
                self.flag = 1
            if self.flag == 1:
                if self.rect.centerx <= r_android.centerx:
                    self.rect.left -= 10
                    if self.rect.right <= r_android.left:
                        self.flag = 2
                else:
                    self.rect.left += 10
                    if self.rect.left >= r_android.right:
                        self.flag = 2
                
        screen.blit(self.img,self.rect)
        return 0


class Sky():
    """
    this is for the background, and show every part of the surface over and over again
    """
    def __init__(self,img,size,pos,speed):
        #variable size is the window's size
        #sub_img is the one part of the surface that we want to show 
        #and as time moves, sub_img changes
        self.img = img
        self.size = size
        self.pos = pos
        self.num = self.img.get_rect().height / speed
        self.count = 1
        self.sub_img = self.img.subsurface(Rect(pos,size))
        self.step = 5

    def update(self,screen):

        self.count += 1
        if self.count % 6 == 0:
            #well, the background changes by every six ticks
            self.pos[1] = (self.pos[1] + speed)%self.img.get_rect().height       
        if self.img.get_rect().height-self.pos[1] < self.size[1]:
            diff = self.img.get_rect().height-self.pos[1]
            self.sub_img = self.img.subsurface(Rect(self.pos,(self.size[0],diff)))
            extra_img = self.img.subsurface(
                Rect((0,0),(self.size[0],self.size[1]-diff)))                
            screen.blit(extra_img,(0,diff))
        else:
            self.sub_img = self.img.subsurface(Rect(self.pos,self.size))
        screen.blit(self.sub_img,(0,0))


class Android():
    """
    the actor in the game, which is Android, you can move it
     by pressing right and left arrow keys
    """
    def __init__(self,img,rect,speed):
        self.ful_img = img
        self.imgs = [self.ful_img.subsurface(Rect((i*157.3,0),(157.3,157)))
                         for i in xrange(3)]
        self.rect = rect
        self.speed = speed
        self.num = 0
        self.ex = 0
        self.dead = 0

    def update(self,screen,dead,press_keys):
        if 1 == dead:          
            return 1
        self.num = 0
        if press_keys[K_LEFT]:
            self.rect.left -= self.speed
            self.num = 1
            if self.rect.left <= 8:
                self.rect.left = 8
                
        if press_keys[K_RIGHT]:
            self.num = 2
            self.rect.left += self.speed
            if self.rect.right >= 592:                
                self.rect.right = 592
               
        screen.blit(self.imgs[self.num],self.rect)
        return 0


class Star(Cloud):

    """
    after the robot touches the stars, it will get more points, that is what this class do
    and its father class is Cloud, for some variables the Cloud has 
    """

    def __init__(self,img,rect,speed):
        Cloud.__init__(self,img,rect,speed)

    def update2(self,screen,r_android,dead):
        if dead == 1:
            return -1
        if self.flag == 1 or self.rect.bottom < 0:
            return 1
        if self.rect.colliderect(r_android):
            #of course, when the robot's rectangle overlaps the stars,
            # the robot will get one more point
            self.flag = 1
            return 2
        else:
            self.count += 1
            if self.count % 6 == 0:
                self.rect.top -= speed
            screen.blit(self.img,self.rect)
            return 0


def makeline(begin,end,ystep):

    """ 
    it is the factory which produces line, but exclude horizontal line 
    which is made by a series of points that are made by every step we set
    """

    width = end[0] - begin[0]
    height = end[1] - begin[1]
    points = []
    p = begin
    if height == 0:
        return []
    if width >=0:
        while p[0] <= end[0] and p[1] <= end[1]:
            points.append(copy.deepcopy(p))
            p[1] += ystep
            p[0] += ystep * width / height        
    else:
        while p[0] >= end[0] and p[1] <= end[1]:
            points.append(copy.deepcopy(p))
            p[1] += ystep
            p[0] += ystep * width / height   
    return points


def moveline(line,ystep):
    #line moves up
    n = 0
    while n < len(line):
        line[n][1] -= ystep
        n += 1


def rectCollideLine(rect,line):
    #function made to judge whether the rect collides points in the line
    n = 0    
    overlap = 0
    while n < len(line):
        if rect.collidepoint(line[n]):
            overlap = 1
            break
        else:
            n += 1
    return overlap


class Line():
    """
    this line is used to define the side of the building that robot will meet
    robot should keep away from them
    """
    def __init__(self,img,rect,ystep,speed):
        self.img = img
        #once you deliver the rect to construct the line
        #and the left building'side has the l_line, right has r_line
        if type(rect) == pygame.Rect:
            self.type = 0
            self.rect = rect
            self.l_line = makeline([rect.x,rect.y],[rect.x,rect.bottom],ystep)
            self.r_line = makeline([rect.right,rect.y],[rect.right,rect.bottom],ystep)
            self.pos = [0,rect.y]
            self.bottom = rect.bottom

        #if your parameter's type is list, ok, it alse can construct the line
        if type(rect) == list:
            if len(rect) == 0:
                return
            self.type = 1
            self.l_line = makeline(rect[0],rect[1],ystep)
            self.r_line = makeline(rect[2],rect[3],ystep)
            self.pos = [0,rect[0][1]]
            self.bottom = rect[3][1]
##        self.speed = speed        
        self.count = 0

    def update2(self,screen,r_android,dead):
        #if robot touches r_line and l_line, it will die, well, that is the rule
        if dead == 1:
            return -1
        if rectCollideLine(r_android,self.l_line) == 1 or rectCollideLine(r_android,self.r_line) == 1:
            return -1
        if self.bottom < 0 :
            return 10
        self.count += 1
        if self.count%6 == 0:            
            moveline(self.l_line,speed)
            moveline(self.r_line,speed)
            self.pos[1] -= speed
            self.bottom -= speed
        screen.blit(self.img,self.pos)
        return 0


def makeStarCloud(stars,clouds):    
    star = stars[random.randint(0,len(stars)-1)]
    star.append(clouds[random.randint(0,len(clouds)-1)])
    return star


def make(stars,index):
    star = stars[index]
    return star


def makeclouds():
    cloud = Cloud(cloud_,Rect(80,500,142,38),speed)
    cloud2 = Cloud(cloud_2,Rect(300,600,102,63),speed)
    cloud3 = Cloud(cloud_3,Rect(140,600,102,63),speed)
    cloud4 = Cloud(cloud_3,Rect(450,600,102,63),speed)
    cloud5 = Cloud(cloud_4,Rect(120,600,142,38),speed)
    clouds = [cloud,cloud2,cloud3,cloud4,cloud5]
    return clouds


def makestars():
    stars = [Star(star_,Rect(280,400+i*41,40,41),speed)for i in xrange(8)]

    stars2 = [Star(star_,Rect(400,600+i*41,40,41),speed)for i in xrange(5)]
    stars2 += [Star(star_,Rect(442,600+i*41,40,41),speed)for i in xrange(5)]

    stars3 = [Star(star_,Rect(120,600+i*41,40,41),speed)for i in xrange(4)]
    stars3 += [Star(star_,Rect(162,600+i*41,40,41),speed)for i in xrange(4)]
    stars3 += [Star(star_,Rect(204,600+i*41,40,41),speed)for i in xrange(4)]

    stars4 = [Star(star_,Rect(300,600+i*41,40,41),speed)for i in xrange(5)]
    stars4 += [Star(star_,Rect(342,600+i*82,40,41),speed)for i in xrange(3)]
    stars4 += [Star(star_,Rect(384,600+i*164,40,41),speed)for i in xrange(2)]

    stars5 = [Star(star_,Rect(200,600+i*41,40,41),speed)for i in xrange(3)]
    stars5 += [Star(star_,Rect(242,600+1*41,40,41),speed)]
    stars5 += [Star(star_,Rect(284,600+i*41,40,41),speed)for i in xrange(3)]

    stars6 = [Star(star_,Rect(100,600+i*41,40,41),speed)for i in xrange(5)]
    stars6 += [Star(star_,Rect(142,641+i*41,40,41),speed)for i in xrange(5)]
    stars6 += [Star(star_,Rect(184,682+i*41,40,41),speed)for i in xrange(5)]

    stars7 = [Star(star_,Rect(222,600+i*41,40,41),speed)for i in xrange(4)]
    stars7 += [Star(star_,Rect(264,600+3*41,40,41),speed)]
    stars7 += [Star(star_,Rect(306,600+i*41,40,41),speed)for i in xrange(4)]

    stars8 = [Star(star_,Rect(150,600+i*41,40,41),speed)for i in xrange(5)]
    stars8 += [Star(star_,Rect(192,600+2*41,40,41),speed)]
    stars8 += [Star(star_,Rect(234,641+i*82,40,41),speed)for i in xrange(2)]
    stars8 += [Star(star_,Rect(275,600+i*41*4,40,41),speed)for i in xrange(2)]

    stars9 = [Star(star_,Rect(400,600+i*41,40,41),speed)for i in xrange(5)]
    stars9 += [Star(star_,Rect(442,600+i*41*2,40,41),speed)for i in xrange(2)]
    stars9 += [Star(star_,Rect(484,600+i*41*2,40,41),speed)for i in xrange(2)]
    stars9 += [Star(star_,Rect(526,600+i*41*2,40,41),speed)for i in xrange(2)]

    stars10 = [Star(star_,Rect(50,600+i*41,40,41),speed)for i in xrange(4)]
    stars10 += [Star(star_,Rect(92,600+3*41,40,41),speed)for i in xrange(1)]
    stars10 += [Star(star_,Rect(134,600+i*41,40,41),speed)for i in xrange(4)]

    allstar = [stars,stars2,stars3,stars4,stars5,stars6,stars7,stars8,stars9,stars10]
    return allstar


def makewall():
    ystep = 1
    wall = Line(buildings_,Rect(192,600,245,432),ystep,speed)
    wall2 = Line(buildings2_,Rect(113,600,237,432),ystep,speed)
    wall3 = Line(buildings3_,Rect(334,600,221,432),ystep,speed)
    wall4 = Line(buildings4_,[[139,600],[85,600+423],[402,600],[357,600+423]],ystep,speed)
    wall5 = Line(buildings5_,[[144,600],[206,600+423],[422,600],[495,600+423]],ystep,speed)
    return [wall,wall2,wall3,wall4,wall5]


def pickwall(walls):
    return walls[random.randint(0,len(walls)-1)]


class StarControl():
    """
    this class is quite important, since it controls all the objects excluding Android

    """
    def __init__(self):
        self.stars = makestars()
        self.clouds = makeclouds()
        self.walls = makewall()
        self.index = 1
        self.star_set = makeStarCloud(self.stars,self.clouds)
        self.flags = [ 0 for i in xrange(len(self.star_set))]
        self.score = 0 

    def update(self,screen,r_android,dead):        
        i = 0
        while i< len(self.star_set):
            #if every object return -1, that means that robot has been dead
            #but if them return 1, they tell that they have move outside the window area
            #and the star will return 2, once the robot touches them or return 1 when they
            #move outside the window area, so that the control center can igonre them
            if self.flags[i] < 0:
                return -1
            if self.flags[i] > 0:
                self.score += self.flags[i] / 2
                self.star_set.pop(i)
                self.flags.pop(i)                
            i += 1  

        for i2 in xrange(len(self.star_set)):
            if self.flags[i2] == 0:
                self.flags[i2] = self.star_set[i2].update2(
                    screen,r_android,dead)

        if len(self.star_set) == 0:
            self.index += 1
##            if self.index%4 == 0:
##                self.clouds = makeclouds()
            if self.index%10 == 0:
                self.stars = makestars()
                self.clouds = makeclouds()
            if self.index%3 == 0:
                self.walls = makewall()
                self.star_set = [pickwall(self.walls)]
            else:
                self.star_set = makeStarCloud(self.stars,self.clouds)
            self.flags = [ 0 for i in xrange(len(self.star_set))]
        return 0


        
#global variables
size=(600,580)
speed = 18
dwTime = 80
goal = 0
pygame.init()    
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size, 0, 32)
pygame.display.set_caption("I believe I can fly !")
cloud_ = pygame.image.load('cloud.png').convert_alpha()
cloud_2 = pygame.image.load('cloud2.png').convert_alpha()
cloud_3 = pygame.image.load('cloud3.png').convert_alpha()
cloud_4 = pygame.image.load('cloud4.png').convert_alpha()
background=pygame.image.load('background.png').convert_alpha()
parachute_ = pygame.image.load('parachute.png').convert_alpha()
star_ = pygame.image.load('star_.png').convert_alpha()
buildings_= pygame.image.load('buildings.png').convert_alpha()
buildings2_= pygame.image.load('buildings2.png').convert_alpha()
buildings3_= pygame.image.load('buildings3.png').convert_alpha()
buildings4_= pygame.image.load('buildings4.png').convert_alpha()
buildings5_= pygame.image.load('buildings5.png').convert_alpha()

font = pygame.font.Font(None, 30)
text = font.render('score:', True, (0, 255, 0))        
sky = Sky(background,size,[0,0],speed)
note = font.render('Sorry,you have touched buildings. :(', True, (138,43,226))
####


def page3():
    
        global speed
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        andr = Android(parachute_,Rect(210,100,157,157),5)
        star_ctrl = StarControl()
        dead = 0

        while True:        
            for event in pygame.event.get():  
                if event.type == QUIT:  
                    pygame.quit()
                    sys.exit()
            press_keys=pygame.key.get_pressed()
            if star_ctrl.score % 30 == 0 and star_ctrl.score != 0:
                speed += 5
            sky.update(screen)           
            andr.update(screen,dead,press_keys)            
            if dead == 0:
                if star_ctrl.update(screen,andr.rect,0) == -1:
                    dead = 1
            if dead == 1:
                screen.blit(note, [145,170])
            score = font.render(str(star_ctrl.score), True, (150, 69 ,0))
            screen.blit(text, [10,8])
            screen.blit(score,[72,9])
            pygame.display.update()
            clock.tick(dwTime)


if __name__ == "__main__":  
    page3()  
