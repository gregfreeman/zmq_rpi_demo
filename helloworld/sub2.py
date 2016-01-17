#!/usr/bin/env python

import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, "")
socket.connect('tcp://localhost:5555')

for i in range(10):
    print(socket.recv())
