#!/usr/bin/env python

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

for i in range(10):
    time.sleep(1)
    socket.send(b"Hello World %d" % i)
