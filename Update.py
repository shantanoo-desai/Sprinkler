#!/usr/bin/python3
from lt import encode, decode

from lt.sampler import DEFAULT_DELTA

from os import chdir, path

from struct import pack, unpack

from twinSocket import *

from math import log, sqrt, ceil

import argparse

import sys


Blocksize = 1452


def addFooter(encodedBlock):
	""" Add at the end of each encoded Block add a 4B footer to indicate Version """

	packedData = encodedBlock + pack('!I', VERSION)
	return packedData

def Fountain(PATH, FILENAME, VERSION):
	""" Main Program that starts/stops the Fountain and anticipates an ACK from the Buckets """


	with open(FILENAME, 'rb') as f:
		# To calculate the size of the File and and the number of blocks
		# the number of the Blocks depends on the "Blocksize" < 1500 B to avoid IPv6
		# Fragments at source and avoid risk of data being deleted from receiver buffer
		
		fileSize, Blocks = encode._split_file(f, Blocksize)
		K = len(Blocks)
		print("FILE SIZE: %d Bytes" %fileSize)
		print("Number of Blocks: ", K)

	"""
	Calculation of Gamma is based on the Paper: The Use and Performance of LT Codes 
	for Multicast with Relaying by Matthew T. Tang, Brooke Shrader & Thomas C. Royster IV

	Gamma is an additional factor which is can assure that a certain number of encoded packets
	such as K' > K is needed to completely decode the file at decoder(Bucket)
	Relation : K' = K(1 + Gamma)
	
	"""
	Gamma = ceil(sqrt(K) * (log(K/DEFAULT_DELTA)**2)/K)


	############################################################################################

	with open(FILENAME, 'rb') as f:

		#Create Socket & Bind it to Multicast Port
		servSocket = twinSocket()
		servSocket.bindTheSock()

		# Counter to check if we are not sending a lot of packets than K'
		packetCounter = 0


		while True:
			print("Starting Fountain \n")

			for eachBlock in encode.encoder(f, Blocksize):
				# Encode each incoming Block with the LT-Encoder scheme
				# Add a 4 Byte footer at end of each block

				dataToSend = addFooter(eachBlock)
				try:
					# Send the packed data to the Multicast Group
					servSocket.sendToSock(dataToSend, MCASTGRP)
					# increase the counter
					packetCounter += 1

					# Check if K' packets are already sent
					if packetCounter not in range((1 + Gamma) * K):
						print("Packets Sent: ", packetCounter)

						# If so Close the Fountain..
						print("Closing Fountain")
						break

				except socket.error as e:
					print("Error in Socket.. closing it!")
					servSocket.closeSock()
			

			# Receiving ACK
			dataACK, fromDestinations = servSocket.recvFromSock(65535)
			if dataACK:
				print("Acknowledgement received")
			break
		
	############################################################################################

	theirVERSION = unpack('!I', dataACK)[0]
	if VERSION == int(theirVERSION):
		print("Compliance!! ")
		servSocket.closeSock()


if __name__ == "__main__":
	parser = argparse.ArgumentParser("Updated")

	parser.add_argument('path', type = str, help = 'Path to your file')

	parser.add_argument('filename', type = str, help = 'Intel HEX file')

	parser.add_argument('version', type = int, default = 1, help = 'Version Number')

	args = parser.parse_args()

	# check path argument
	if not path.exists(args.path):
		print("Path doesn't exists", file = sys.stderr)
		sys.exit(1)
	PATH = args.path
	chdir(PATH)

	# check file argument 
	if not path.isfile(args.filename):
		print("File doesn't exists", file = sys.stderr)
		sys.exit(1)
	FILENAME = args.filename


	VERSION = args.version

	Fountain(PATH, FILENAME, VERSION)