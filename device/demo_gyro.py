#!/usr/bin/env python

from __future__ import print_function
from Adafruit_L3GD20 import Adafruit_L3GD20
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import zmq
import json
from quaternion import Quaternion, dqdT
from numpy import array
from math import pi


gyr = Adafruit_L3GD20()

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
port = 5559
pub.bind("tcp://*:%s" % port)

state = {}
state['q'] = Quaternion.identity()
state['gyrobias'] = array([-1.7700930656934308, -5.679372718978101,  -0.9736322992700736])
cbias = 0.005
ts = 0.05


def task20Hz():
    w = array(gyr.read())
    q = state['q']
    gyrobias = state['gyrobias']

    q = dqdT(q, (w-gyrobias)*pi/180, ts)
    q.normalize()
    gyrobias = cbias*w + (1-cbias)*gyrobias

    state['q'] = q
    state['gyrobias'] = gyrobias

    data = {'x': w[0],
            'y': w[1],
            'z': w[2],
            'q': list(q.q)}
    pub.send(json.dumps(data))

lc = LoopingCall(task20Hz)
lc.start(ts)

print('starting demo')
reactor.run()
