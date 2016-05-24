#!/usr/bin/python3

from lt import encode, decode

from lt.sampler import DEFAULT_DELTA

from os import chdir, path

from struct import pack, unpack

from twinSocket import *

from trickle import trickleTimer

from math import log, sqrt, ceil

import argparse

import sys

import datetime

import time

import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

Blocksize = 1452

def addFooter(encodedBlock):
    """ Add at the end of each LT-encoded Block add a 2B footer to indicate Version """

    packedData = encodedBlock + pack('!H', VERSION)
    return packedData




def Fountain(PATH, FILENAME, VERSION):
    """ Main Program that starts/stops the Fountain and
        anticipates an ACK from the Buckets if File is
        Decoded..
        If File is not decoded at the Receiver then a 
        Socket Timeout will trigger a NACK to indicate
        the Fountain that a bit more packets are needed
    """

    ##   Determination of Parameters ##

    with open(FILENAME, 'rb') as f:
        """ To calculate the size of the File and and the number of blocks
            the number of the Blocks depends on the "Blocksize" < 1500 B to avoid IPv6
            Fragments at source and avoid risk of data being deleted from receiver buffer
        """
        
        fileSize, Blocks = encode._split_file(f, Blocksize)
        K = len(Blocks)
        logging.info("FILE SIZE: %d Bytes" %fileSize)
        logging.info("Number of Blocks: %d" %K)

    """
        Calculation of Gamma is based on the Paper: 
        The Use and Performance of LT Codes for Multicast with Relaying 
        by Matthew T. Tang, Brooke Shrader & Thomas C. Royster IV

        Gamma is an additional factor which is can assure that a certain number of encoded packets
        such as K' > K is needed to completely decode the file at decoder(Bucket)
        Relation : K' = K(1 + Gamma)
    
    """
    Gamma = ceil(sqrt(K) * (log(K/DEFAULT_DELTA)**2)/K)

    
    ## Starting a Fountain ##

    with open(FILENAME, 'rb') as f:
        """ 
            1. Parse the Complete Input File
            2. Encode Each Packet
            3. Add Footer
            4. Send it to Multicast Port (ff02::1, 30001)
            5. Check for the Upper Bound and once crossed close Fountain
            6. Listen on Port for NACK/ACK from Buckets
            7. If(ACK) - Do Nothing / Else Start Fountain again
        """
        #Create Socket & Bind it to Multicast Port
        servSocket = twinSocket()
        servSocket.bindTheSock()

        # Counter to check if we are not sending a lot of packets than K'
        packetCounter = 0


        while True:
            timeStamp1 = datetime.datetime.now().replace(microsecond=0)
            logging.info("Starting Fountain")

            for eachBlock in encode.encoder(f, Blocksize):
                # Encode each incoming Block with the LT-Encoder scheme
                # Add a 2 Byte footer at end of each block
                dataToSend = addFooter(eachBlock)

                try:
                    # Send the Packet
                    servSocket.sendToSock(dataToSend,MCASTGRP)
                    # Count the number of Packets sent
                    packetCounter += 1

                    # If packets reach the Upper Bound Close the Fountain
                    if (packetCounter >= ((1+Gamma)*K)):
                        timeStamp2 = datetime.datetime.now().replace(microsecond=0)
                        logging.info("Packets Sent: %d" %packetCounter)
                        logging.info("Time needed: %s" %str(timeStamp2 - timeStamp1))
                        logging.info("Closing Fountain")
                        break

                except socket.error as e:
                    # Exception Raise
                    raise e
                    servSocket.closeSock()
            txtt = trickleTimer(servSocket.sendToSock,{'message': pack('!H', VERSION), 'host': MCASTGRP,\
                         'port': MCASTPORT}, 0.1, 8)
            txtt.start()
            while True:
                #Once Fountain is closed listen for NACK/ACKS from Buckets

                response, Buckets = servSocket.recvFromSock(512)

                if not response:
                    # If not response type
                    break

                # Print the Bucket Address
                #print(Buckets)

                #Version Check
                theirVersion = unpack('!I', response)[0]
                if theirVersion == VERSION:
                    logging.info("Compliance")
                    txtt.hear_consistent()
                else:
                    # If Bucket has a Timeout then Start the Fountain Again
                    logging.info("Non Compliance")
                    txtt.hear_inconsistent()
                    time.sleep(5)
                    Fountain(PATH, FILENAME, VERSION)
        
    ############################################################################################

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Fountain")

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

    # Version
    VERSION = args.version

    Fountain(PATH, FILENAME, VERSION)