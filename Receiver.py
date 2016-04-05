from sys import argv, exit
import os, time
from twinSocket import *
from trickle import trickleTimer
from struct import pack, unpack, unpack_from
from message_constants import MSGVERSION, DATALEN

IMIN  = 0.1
IMAX = 8

def rxconsistencyCheck(version, datalen, trickTimer):
	"""if consistent return True --> do not save Hex Code 
	if not consistent return False --> Save Hex code from payload
	"""
	global MSGVERSION

	if(int(version) == MSGVERSION):
		print "Consistent Version..."
		trickTimer.hear_consistent()
		return True

	elif (int(version) < MSGVERSION):
		print "Their Version is Lagging.."
		print "Inconsistency detected.."
		trickTimer.hear_inconsistent()
	else:
		print "Our Version is Lagging.."
		print "Updating our Version.."
		MSGVERSION = int(version)
		trickTimer.hear_inconsistent()
	
	print "Their Version:%d Our Version:%d now.. " %(version, MSGVERSION)
	return False
	global DATALEN

	if(int(datalen) == 0):
		print "No further Data: ACK.."

	else:
		print "there is some data.."

def receiver():
	print "Starting Receiver Mode\n"
	PIPATH = '/home/testbed/'

	# --------------- Socket for Receiving
	recvSocket = twinSocket()
	recvSocket.bindTheSock()
	myDATALEN = 0 # I wont send any day in return..
	reply = pack('!IH', MSGVERSION, DATALEN)

	rxtt = trickleTimer(recvSocket.sendToSock, {'message': reply, 'host': MCASTGRP, 'port': MCASTPORT}, \
		IMIN, IMAX)
	rxtt.start()

	while True:
		dataRecv, fromSource = recvSocket.recvFromSock(65535)

		if not dataRecv:
			break

		print "-----------------------------\n"
		print "data received from: ", fromSource
		theirVersion, theirDataLen = unpack_from('!IL', dataRecv)
		hexFILE = dataRecv[8:]
		# Check DATA...
		constFlag = rxconsistencyCheck(theirVersion, theirDataLen, rxtt)

		if constFlag:
			print "Consistent not Writing hexfile"
		elif hexFILE:
			print "Writing hexfile..."
			os.chdir(PIPATH)
			newHexFile = open('newHexFile.txt', 'w')
			newHexFile.write(hexFILE)
			newHexFile.close()
			
			myDATALEN = 0 # As a way to create an ACK and I have no data
			print MSGVERSION
		rxtt.cancel()
		reply = pack('!IH', MSGVERSION, myDATALEN)
		rxtt = trickleTimer(recvSocket.sendToSock, {'message': reply, 'host': MCASTGRP, 'port': MCASTPORT}, \
		IMIN, IMAX)
		rxtt.start()
	
	recvSocket.closeSock()