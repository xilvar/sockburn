#from gevent import monkey
#monkey.patch_all()

import argparse
import socket
import ometer

ITERATIONS = 102400
BUFSIZE = 102400

PORT = 6666
INTERFACE = "0.0.0.0"
REMOTE = "127.0.0.1"

def send(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    buf = BUFSIZE * "\0"
    om = ometer.OMeter("MB", ITERATIONS*BUFSIZE/1024.0/1024.0)
    for i in xrange(ITERATIONS):
        s.sendall(buf)
        om.iteration(BUFSIZE/1024.0/1024.0)
    s.close()

def receive(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((INTERFACE, port))
    s.listen(1)
    total = 0
    conn, addr = s.accept()
    om = ometer.OMeter("MB", ITERATIONS*BUFSIZE)
    while total < ITERATIONS*BUFSIZE:
        data = conn.recv(BUFSIZE)
        actual = len(data)
        total += actual
        om.iteration(actual/1024.0/1024.0)
    conn.close()

def run():
    p = argparse.ArgumentParser(description="send a lot of data on a socket")
    p.add_argument('mode', choices=["s","r"])
    p.add_argument('--host', default=REMOTE)
    p.add_argument('--port', default=PORT)

    ns = p.parse_args()
    if ns.mode == "s":
        send(ns.host, ns.port)
    elif ns.mode == "r":
        receive(ns.port)

        #send()
    #receive()

run()
