#!/usr/bin/python3

from lt import encode, decode

from lt.sampler import DEFAULT_DELTA

from struct import pack, unpack

from math import log, sqrt, ceil

from twinSocket import *

from trickle import trickleTimer

from os import chdir, path

import argparse, sys, datetime, logging, threading

# Trickle Parameters Optimized for Setup
IMAX = 4
IMIN = 9

# Logging Configuration
logger = logging.getLogger("Fountain")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('fountain.log')
handler.setLevel(logging.DEBUG)

# format for logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def addFooter(encodedBlock, VERSION):
    """concatenate a 2B Version after each LT-encoded Block"""

    packedData = encodedBlock + pack('!H', VERSION)
    return packedData


def fountainParameters(FILENAME, BLOCKSIZE):
    """Calculation of Parameters for Controlling the Fountain
       Returns the K and Gamma
    """

    with open(FILENAME, 'rb') as f:

        sizeOfFile, blockCount = encode._split_file(f, BLOCKSIZE)

        calcK = len(blockCount)

        logger.debug("No. of Blocks: %d" %calcK)
        logger.debug("FileSize in bytes: %d" %sizeOfFile)

        calcGamma =  ceil(sqrt(calcK) * (log(calcK/DEFAULT_DELTA)**2)/calcK)
        logger.debug("Gamma: %d" %calcGamma)

    return calcK, calcGamma


def checkConsistency(theirVersion, VERSION, founTT):
    """Function to check trickle message consistency RFC6206"""

    if theirVersion == VERSION:
        logger.debug("their Version:%d, our Version:%d"%(theirVersion,VERSION))
        logger.info("Consistency Detected")
        founTT.hear_consistent()
    else:
        logger.debug("their Version:%d, our Version:%d"%(theirVersion,VERSION))
        logger.info("Inconsistency Detected")
        founTT.hear_inconsistent()

        # If theirs and our VERSION values don't match Start the Fountain Again
        # THREAD here... NOT SURE IF GOOD IDEA HERE
        fThread = threading.Thread(target = fountain, args=(FILENAME, BLOCKSIZE, VERSION), daemon=True)
        fThread.start()
        fThread.join()
    logger.info("Exiting the Check")

def fountain(FILENAME, BLOCKSIZE, VERSION):
    """Main Fountain code: will send encoded Packets upto a certain
       limit over a multicast channel
    """

    # Bring in the Fountain Paramaters
    K, Gamma = fountainParameters(FILENAME, BLOCKSIZE)

    with open(FILENAME, 'rb') as f:
        """
            Methodology for Fountain:
            1. parse the Input file
            2. encode each block and add footer
            3. send the droplet(block)
            4. control the fountain using the limit K'=(1+Gamma)K
            5. start the trickle timer for consistency check
            6. anticipate the trickle messages from buckets
            7. based on in/consistency restart/listen
        """

        packetCounter = 0

        while (1):

            timeStamp1 = datetime.datetime.now().replace(microsecond=0)
            logger.info("Starting Fountain")

            for eachBlock in encode.encoder(f, BLOCKSIZE):
                # Step : 2
                droplet = addFooter(eachBlock, VERSION)

                try:
                    # Step : 3
                    fSocket.sendToSock(droplet, MCASTGRP)
                    packetCounter += 1

                    # Step : 4
                    if( packetCounter >= (1+Gamma)*K ):
                        timeStamp2 = datetime.datetime.now().replace(microsecond=0)

                        logger.debug("Droplets Sent: %d" %packetCounter)
                        logger.debug("Time Needed: %s" %str(timeStamp2 - timeStamp1))
                        logger.info("Closing Fountain")
                        break

                except socket.error as sockE:
                    raise sockE
                    fSocket.closeSock()

            # Out of the encoder block
            # Step : 5
            # start the Trickle Timer by sending our Current Code Version

            founTT = trickleTimer(fSocket.sendToSock, {'message': pack('!H', VERSION), 'host': MCASTGRP, 'port': MCASTPORT}, IMAX, IMIN)

            founTT.start()
            Cognition(fSocket, VERSION, founTT) # IS THIS HACKY OR GOOD??

def Cognition(fSocket, VERSION, founTT):
    logger.info("Entering Cognition State")

    while True:
        """Go in to Cognition(Receiving) State for Consistency Check"""
        # Step : 6
        print("Cognition state")

        response, Buckets = fSocket.recvFromSock(512)

        if not response:
            break
        try:
            bucketName = fSocket.getLocalName(Buckets)
            logger.info("message from-------%s" %bucketName)

        except socket.herror:
                pass
        else:
            # Unpack the trickleMessage
            theirVersion = unpack('!H', response)[0]
            
            # Step : 7 USING a Thread called Checker. Assuming once Thread is
            # done checking it returns back here.. Back to Cognition state
            checker = threading.Thread(target=checkConsistency, args=(theirVersion, VERSION, founTT), daemon=True)
            checker.start()
            checker.join()
     

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Fountain")

    parser.add_argument('path', type = str, help = 'path to file')
    parser.add_argument('filename', type = str, help = 'name of file')
    parser.add_argument('version', type = int, help = 'version number')
    parser.add_argument('blocksize', type = int, help = 'mtu size < 1500 B')

    args = parser.parse_args()

    if not path.exists(args.path):
        print("Path doesn't exist", file = sys.stderr)
        sys.exit(1)
    chdir(args.path)

    if not path.isfile(args.filename):
        print("File doesn't exist", file = sys.stderr)
        sys.exit(1)

    FILENAME = args.filename
    VERSION = args.version
    BLOCKSIZE = args.blocksize

    # Open A MCAST socket and Bind it
    fSocket = twinSocket()
    fSocket.bindTheSock()
    
    fountain(FILENAME, BLOCKSIZE, VERSION)