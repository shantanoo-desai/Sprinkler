from sys import argv, exit, stdin
import os, time
from twinSocket import *
from lt import decode

def receiver():
	print("Starting Receiver Mode\n")
	# this the path on Pi where the "INOTIFY-TOOLS" has been set
	#PIPATH = '/home/pi/contiki-2.7/tools/z1/'
	PIPATH = '/tmp/'
	# this is the filename on which the "INOTIFY-TOOLS" will react.
	PIFILENAME = 'main.ihex'

	# --------------- Socket for Receiving
	recvSocket = twinSocket()
	recvSocket.bindTheSock()

	while True:
		# Data received from the server and/or other clients
		dataRecv, fromSource = recvSocket.recvFromSock(65535)

		print("-----------------------------\n")
		print("data received from: ", fromSource)
		
		
		decode.run(dataRecv)

		
	
	recvSocket.closeSock()


if __name__ == '__main__':
	receiver()