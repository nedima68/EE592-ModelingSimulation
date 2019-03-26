"""
@author Dr. M. Nedim ALPDEMİR
"""
from vpython import *
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import time

class ConveyorType:
    IN = "IN"
    OUT = "OUT"

class ConveyorBelt3D():
    def __init__(self, scene, c, vis_slots = 4, l=8, w=1.2, h=1, direction=vector(1,0,0), type=ConveyorType.IN):

        leg_color = vector(0,0,0.2)
        belt_color = vector(0.8,0.8,0.9)
        self.dir = direction # this should be a vpython vector
        self.numVisibleSlots = vis_slots
        self.slotSize = l / (self.numVisibleSlots*2) # length / slot number
        # create the 4 legs
        self.left_fl = box(pos=vector(c.x-l/2,c.y,c.z-w/2.0), size=vector(w*0.1,h,w*0.1), color=leg_color, canvas = scene)
        self.left_bl = box(pos=vector(c.x-l/2,c.y,c.z+w/2.0), size=vector(w*0.1,h,w*0.1), color=leg_color, canvas = scene)
        self.right_fl = box(pos=vector(c.x+l/2,c.y,c.z-w/2.0), size=vector(w*0.1,h,w*0.1), color=leg_color, canvas = scene)
        self.right_bl = box(pos=vector(c.x+l/2,c.y,c.z+w/2.0), size=vector(w*0.1,h,w*0.1), color=leg_color, canvas = scene)
        # create top belt
        self.topBelt = box(pos=vector(c.x,c.y+h/2.0,c.z), size=vector(l,h*0.1,w), color=belt_color, canvas = scene)
        self.leftEndPt = vector(self.topBelt.pos.x - l/2, self.topBelt.pos.y +  self.topBelt.size.y / 2.0, self.topBelt.pos.z)
        self.rightEndPt = vector(self.topBelt.pos.x + l/2, self.topBelt.pos.y +  self.topBelt.size.y / 2.0, self.topBelt.pos.z)
        self.itemTrain = []
        self.scene = scene
        self.convType = type

    def addItem(self, obj):
        sz = obj.getSize()
        if (self.convType == ConveyorType.IN):
            l = len(self.itemTrain)
            if l > 0:
                endObjPos = self.itemTrain[l-1].cube.pos
                x = endObjPos.x - sz.x - self.slotSize
            else:
                x = self.rightEndPt.x - sz.x - self.slotSize
        elif (self.convType == ConveyorType.OUT):
            x = obj.cube.pos.x
        ItemNewPos = vector(x, self.leftEndPt.y + sz.y / 2, self.leftEndPt.z)
        obj.setPos(ItemNewPos)
        self.itemTrain.append(obj)
        if (self.convType == ConveyorType.IN):
            if len(self.itemTrain) > self.numVisibleSlots:
                obj.setVisible(False)
            else:
                obj.setVisible(True)


    def getItem(self):
        if len(self.itemTrain) > 0:
            item = self.itemTrain.pop(0)
            if len(self.itemTrain) >= self.numVisibleSlots:
                self.itemTrain[self.numVisibleSlots-1].setVisible(True)
            return item
        else:
            return None

    def moveBelt(self):
        t = np.linspace(0,2,40)
        dt = t[1]-t[0]
        for i in range(len(t)):
            rate(1/dt)
            for obj in self.itemTrain:
                obj.move((self.dir * self.slotSize/2.0) * dt)
        if (self.convType == ConveyorType.OUT):
            if len(self.itemTrain) > self.numVisibleSlots:
                obj = self.itemTrain.pop(0)
                obj.setVisible(False)
                del obj

class CraneStateType:
    IDLE = "IDLE"
    MOVING_OBJECT = "MOVING_OBJECT"
    RETURN_BACK = "RETURN_BACK"

class CraneObj3D:
    # c= center postion, sh=height (along y axis), sl=length (along x axis), sw=width (along z axis)
    def __init__(self, scene, c=vector(1,0,-1), sl=7, sh=4,sw=3,color=vector(1,0,0)):
        self.state = CraneStateType.IDLE
        self.cart_h=sh*0.05
        self.cart_w=sw*0.53
        self.cart_l=sw*0.25

        # define cart operating range in terms of two points (left end, right end).
        # These points are used  to define  object pick up and release points
        self.cart_op_range = (vector(c.x-sl/2+sw*0.1+sw*0.125, c.y, c.z),
                                     vector(c.x+sl/2-sw*0.1-sw*0.125, c.y, c.z))
        self.cart_pos = vector(self.cart_op_range[0].x,c.y+sh/2,c.z)
        leg_color = vector(0,0,0)
        # create the 4 legs
        self.left_fl = box(pos=vector(c.x-sl/2,c.y,c.z-sw/2), size=vector(sw*0.1,sh,sw*0.1), color=leg_color, canvas = scene)
        self.left_bl = box(pos=vector(c.x-sl/2,c.y,c.z+sw/2), size=vector(sw*0.1,sh,sw*0.1), color=leg_color, canvas = scene)
        self.right_fl = box(pos=vector(c.x+sl/2,c.y,c.z-sw/2), size=vector(sw*0.1,sh,sw*0.1), color=leg_color, canvas = scene)
        self.right_bl = box(pos=vector(c.x+sl/2,c.y,c.z+sw/2), size=vector(sw*0.1,sh,sw*0.1), color=leg_color, canvas = scene)
        # create the 4 top bars
        self.front = box(pos=vector(c.x, c.y+sh/2, c.z-sw/3), size=vector(sl, sh*0.03, sw*0.1), color=vector(color), canvas = scene)
        self.back = box(pos=vector(c.x, c.y+sh/2, c.z+sw/3), size=vector(sl, sh*0.03, sw*0.1), color=vector(color), canvas = scene)
        self.left = box(pos=vector(c.x-sl/2, c.y+sh/2, c.z), size=vector(sw*0.1, sh*0.03, sw), color=vector(color), canvas = scene)
        self.right = box(pos=vector(c.x+sl/2, c.y+sh/2, c.z), size=vector(sw*0.1, sh*0.03, sw), color=vector(color), canvas = scene)
        # create crane cart
        cart_color = vector(1,1,0)

        self.cart = box(pos=self.cart_pos, size=vector(self.cart_l,self.cart_h,self.cart_w), color=cart_color, canvas = scene)
        # create pendulum
        self.plength = sh*0.5
        self.pend_pos = vector(self.cart_pos.x, self.cart_pos.y - (self.plength/2.0), self.cart.pos.z)
        self.pend_end_pos = vector(self.pend_pos.x, self.pend_pos.y- (self.plength /2.0) , self.pend_pos.z)
        self.pend = box(pos=self.pend_pos, size=vector(self.plength*0.03, self.plength ,self.plength*0.03), color=vector(color)*0.2, canvas = scene)

    def pickItem(self, obj):
        pickPt = vector(self.pend_pos.x, obj.pos.y , self.pend_pos.z)
        xr = pickPt.x - obj.pos.x
        if (xr > 0):
            res = 40 # resoluton of the time axis. 50 time points
            sec = 2.0 # move in 2 seconds
            t = np.linspace(0,sec,res)
            v = np.full((1,res),xr/res)[0]
            dt = t[1] - t[0]
            for i in range(len(t)):
                rate(1/dt)
                obj.pos.x += v[i]

        obj.pos = vector(self.pend_pos.x, self.pend_pos.y- (self.plength /2.0) , self.pend_pos.z)

    def stepMoveObject(self, dt, theta_i, d_theta, vel_i, obj):
        rate(1/dt)
        self.pend.rotate(angle=d_theta,  axis=vec(0,0,1), origin=vector(self.cart.pos.x, self.cart.pos.y, self.cart.pos.z ))
        obj.pos.x = self.cart.pos.x - self.plength * np.cos(math.pi/2.0 + theta_i)
        obj.pos.y = self.cart.pos.y-self.cart_h/2.0 - self.plength * np.sin(math.pi/2.0 + theta_i)
        self.cart.pos.x += vel_i
        self.pend.pos.x += vel_i
        obj.pos.x += vel_i

    def move_obj(self, time, theta, theta_dot, vel, obj):
        """ This function makes the crane pick an object from left end of its operational range and
        move it to the other end (right) of its op range."""
        dt = time[1] - time[0]
        d_th_o = theta[1]-theta[0]

        for i in range(len(time)):
            rate(1/dt)
            if (i<2):
                d_th = d_th_o
            else:
                d_th = theta[i]-theta[i-1]

            self.pend.rotate( angle=d_th,  axis=vec(0,0,1), origin=vector(self.cart.pos.x, self.cart.pos.y, self.cart.pos.z ))
            obj.pos.x = self.cart.pos.x - self.plength*np.cos(math.pi/2.0 + theta[i])
            obj.pos.y = self.cart.pos.y-self.cart_h/2.0 - self.plength*np.sin(math.pi/2.0 + theta[i])

            self.cart.pos.x += vel[i]
            self.pend.pos.x += vel[i]
            obj.pos.x += vel[i]

    def moveBack(self, seconds):
        resolution = 100
        self.t_back_move = np.linspace(0,seconds,resolution)
        self.v_back_move = np.full((1,resolution),(self.cart_op_range[1].x - self.cart_op_range[0].x)/(resolution-1))[0]
        dt = self.t_back_move[1] - self.t_back_move[0]
        for i in range(len(self.t_back_move)):
            rate(1/dt)
            self.cart.pos.x -= self.v_back_move[i]
            self.pend.pos.x -= self.v_back_move[i]

class Item3D:
    def __init__(self, id, scene, sizeVec, posVec):
        self.id = id
        #col = vector(0.9, 0.1, 0.1)
        col = vector(random.uniform(0.2,0.9), random.uniform(0.2,0.9), random.uniform(0.2,0.9))
        self.cube = box(pos=vector(posVec), size=vector(sizeVec), color=vector(col), canvas = scene)

    def delete(self):
        self.cube.visible = False
        del self.cube

    def setPos(self, pos):
        self.cube.pos = pos

    def getSize(self):
        return self.cube.size

    def move(self, vec):
        self.cube.pos += vec

    def setVisible(self, vis=False):
        self.cube.visible=vis


    def fromCraneReleasePoint(self, crane_rpt):
        x_r = self.cube.pos.x
        res = 100 # resoluton of the time axis. 50 time points
        sec = 5.0 # move in 3 seconds
        t = np.linspace(0,sec,res)
        v = np.full((1,res),xr/res)[0]
        dt = t[1] - t[0]
        for i in range(len(t)):
            rate(1/dt)
            self.cube.pos.x += v[i]
        self.cube.pos.y = crane.ppt.y

class Scene3D():
    def __init__(self):
        self.scene = canvas() # This is needed in Jupyter notebook and lab to make programs easily rerunnable
        self.scene.title = "A display of 3D Shop Floor Simulation"
        self.scene.width = 740
        self.scene.height = 400
        #scene.range = 5
        self.scene.background = color.gray(0.9)
        self.scene.center = vector(0,0.0,0)
        self.scene.forward = vector(0,0,-1)
        flr = box(pos=vector(.25,-1.8,0), size=vector(44.0,0.05,20.0), color=vector(0.2,0.5,0.6), canvas=self.scene)
        self.sceneObjects = []

    def getRootScene(self):
        return self.scene

    def createMovingObj(self, item):
        edge = item.mass / 20.0
        sz = vector(edge,edge,edge)
        obj = Item3D(item.id, self.scene, sizeVec=sz, posVec = vector(0,0,0))
        obj.setVisible(False)
        return obj

    def updateObjects(self, dt):
        for obj in self.sceneObjects:
            obj.updateBehaviour(dt)

def localTest():
    sc = Scene3D()
    class item():
        def __init__(self, id, m):
            self.mass = m
            self.id = id
    i1 = item(1, 5)
    i2 = item(2, 8)
    i3 = item(3, 10)
    i4 = item(4, 4)
    i5 = item(5, 6)
    i6 = item(6, 18)
    mi1 = sc.createMovingObj(i1)
    mi2 = sc.createMovingObj(i2)
    mi3 = sc.createMovingObj(i3)
    mi4 = sc.createMovingObj(i4)
    mi5 = sc.createMovingObj(i5)
    mi6 = sc.createMovingObj(i6)
    conv = ConveyorBelt3D(sc.getRootScene(), vector(0,-1.3,0), type=ConveyorType.OUT)

    conv.addItem(mi1)
    conv.addItem(mi2)
    conv.addItem(mi3)
    conv.addItem(mi4)
    conv.addItem(mi5)
    conv.addItem(mi6)
    time.sleep(1.0)
    conv.moveBelt()
    #---------------
    #time.sleep(1.0)
    #i = conv.getItem()
    #i.setVisible(False)
    time.sleep(1.0)
    conv.moveBelt()
    #---------------
    time.sleep(1.0)
    #i = conv.getItem()
    #i.setVisible(False)
    #time.sleep(1.0)
    conv.moveBelt()
    #---------------
    time.sleep(1.0)
    #i = conv.getItem()
    #i.setVisible(False)
    #time.sleep(1.0)
    conv.moveBelt()

#localTest()
