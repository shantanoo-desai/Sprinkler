from sys import argv, exit
import os, time
from twinSocket import *
from trickle import trickleTimer
from struct import pack, unpack, unpack_from
from message_constants import MSGVERSION, DATALEN

# Trickle Timer Parameters -- These values are close to ~ 25 seconds
# change for robust usage
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
	# this the path on Pi where the "INOTIFY-TOOLS" has been set
	PIPATH = '/home/pi/contiki-2.7/tools/z1/'
	# this is the filename on which the "INOTIFY-TOOLS" will react.
	PIFILENAME = 'main.ihex'

	# --------------- Socket for Receiving
	recvSocket = twinSocket()
	recvSocket.bindTheSock()
	myDATALEN = 0 # I wont send any day in return.. Kind of an ACK
	# pack data to be sent as a REPLY..
	reply = pack('!IH', MSGVERSION, DATALEN)

	print "Starting trickle Timer....\n"
	rxtt = trickleTimer(recvSocket.sendToSock, {'message': reply, 'host': MCASTGRP, 'port': MCASTPORT}, \
		IMIN, IMAX)
	rxtt.start()

	while True:
		# Data received from the server and/or other clients
		dataRecv, fromSource = recvSocket.recvFromSock(65535)

		if not dataRecv:
			# close socket..
			break

		print "-----------------------------\n"
		print "data received from: ", fromSource

		# Unpack the received data
		theirVersion, theirDataLen = unpack_from('!IL', dataRecv)
		# if data from server, save the hexcode payload
		hexFILE = dataRecv[8:]

		# Check DATA...
		constFlag = rxconsistencyCheck(theirVersion, theirDataLen, rxtt)

		if constFlag:
			# if consistent everytime do not keep writing the same hexfile
			print "Consistent not Writing hexfile"
		# if not consistent then write the new hexfile
		elif hexFILE:
			print "Writing hexfile..."
			os.chdir(PIPATH)
			newHexFile = open(PIFILENAME, 'w')
			newHexFile.write(hexFILE)
			newHexFile.close()
			
			myDATALEN = 0 # As a way to create an ACK and I have no data
			#print MSGVERSION  		<--------------- DEBUG CHECK FOR VERSION
			
		rxtt.cancel()
		# create a new reply as an ACK with no DATALEN
		reply = pack('!IH', MSGVERSION, myDATALEN)
		rxtt = trickleTimer(recvSocket.sendToSock, {'message': reply, 'host': MCASTGRP, 'port': MCASTPORT}, \
		IMIN, IMAX)
		rxtt.start()
	
	recvSocket.closeSock()