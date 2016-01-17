#!/usr/bin/env python

import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, "")
socket.connect('tcp://localhost:5555')
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

while socket in dict(poller.poll(2000)):
    print(socket.recv())
