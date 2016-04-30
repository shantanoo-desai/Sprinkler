from io import BytesIO
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

	# Instantiate an LtDecoder 
	decoder = decode.LtDecoder()

	while True:
		# Data received from the server and/or other clients
		dataRecv, fromSource = recvSocket.recvFromSock(65535)

		print("-----------------------------\n")
		print("data received from: ", fromSource)

		  # Kinda hacky, read a single block as a one-element sequence of blocks using the BytesIO file-like interface for bytes
		lt_block = next(decode.read_blocks(BytesIO(dataRecv)))

		# Feed the block to the decoder, returns true if decoding is complete
		if decoder.consume_block(lt_block):
		    print("Decoded file")

		    # Extract the decoded file and print
		    print(decoder.bytes_dump())
		    exit(0)
		
	
	recvSocket.closeSock()


if __name__ == '__main__':
	receiver()
