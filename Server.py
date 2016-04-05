from sys import argv, exit
import os, time
from twinSocket import *
from trickle import trickleTimer
from struct import pack, unpack, unpack_from
from message_constants import MSGVERSION, DATALEN

IMIN  = 0.1
IMAX = 8

def txconsistencyCheck(version, datalen, trickTimer):
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


def server(PATH, FILENAME):

	print "Starting Server Mode\n"

	#------------PATH CHECK ------------------
	pathFLAG = os.path.exists(PATH)

	if not pathFLAG:
		print "Mentioned path does not exist. Check Again\n"
		exit(1)
	else:
		print "Path exists.. checking file..\n"
		# change into the given path
		os.chdir(PATH)

	#------------ FILE CHECK -----------------
	fileFlag = os.path.isfile(FILENAME)

	if not fileFlag:
		print "Mentioned File does not exist. Check Again\n"
		exit(1)
	else:
		print "File exists..\n"

	# Intel HEXCODE here
	myHEXCODE = open(FILENAME)
	DATALEN = os.stat(FILENAME).st_size
	# -------------- Socket for Sending 
	servSocket = twinSocket()

	servSocket.bindTheSock()

	dataToSend = pack('!IL', MSGVERSION, DATALEN) + str(myHEXCODE.read())

	print "Setting Up Trickle Timer..\n"
	tt = trickleTimer(servSocket.sendToSock, {'message': dataToSend, 'host': MCASTGRP, 'port': MCASTPORT}, \
		IMIN, IMAX)
	tt.start()

	while True:
		dataGot, fromWhom = servSocket.recvFromSock(65535)
		print "----------------------------\n"
		print "data received from: ", fromWhom

		if not dataGot:
			break
				
		theirVersion, theirDataLen = unpack_from('!IH', dataGot)
		additionalData = dataGot[8:0]
		# CHECK DATA....
		constFlag = txconsistencyCheck(theirVersion, theirDataLen, tt)

		if constFlag:
			print "Consistent.. Not writing data.."
			tt.cancel()
			DATALEN = 0 # Kind of ACK
			reply = pack('!IL', MSGVERSION, DATALEN)
			tt = trickleTimer(servSocket.sendToSock, {'message': dataToSend, 'host': MCASTGRP, 'port': MCASTPORT}, \
			IMIN, IMAX)
			tt.start()
		
		elif additionalData:
			print "Writing data to a file....\n"
			os.chdir(PATH)
			newFile = open(newData.txt, 'w')
			newFile.write(additionalData)
			newFile.close()

	servSocket.closeSock()
