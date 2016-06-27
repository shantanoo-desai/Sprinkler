"""
 TWIN Node - A Flexible Wireless Sensor Network Testbed
*
* Copyright (C) 2016, Communication Networks, University of Bremen, Germany
*
* This program is free software; you can redistribute it and/or modify it
* under the terms of the GNU General Public License as published by the
* Free Software Foundation; version 3 of the License.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
* or FITNESS FOR A PARTICULAR PURPOSE.
* See the GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along
* with this program; if not, see <http://www.gnu.org/licenses/>
*
* This file is part of TWIN project
"""

#!/usr/bin/python3

from lt import encode, decode

from lt.sampler import DEFAULT_DELTA

from struct import pack, unpack

from math import log, sqrt, floor

from twinSocket import *

from trickle import trickleTimer

from os import chdir, path

import argparse, sys, datetime, logging, threading, time

import global_variables as gv

# Logging Configuration
logger = logging.getLogger("Fountain")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('./logFiles/fountain.log')
handler.setLevel(logging.DEBUG)

# format for logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


fSocket = twinSocket()


def addFooter(encodedBlock, VERSION):
    """concatenate a 2B Version after each LT-encoded Block"""

    packedData = encodedBlock + pack('!H', VERSION)
    return packedData


def fountainParameters(FILENAME, BLOCKSIZE):
    """Calculation of Parameters for Controlling the Fountain
       Returns the K and Gamma
    """

    with open(FILENAME, 'rb') as f:

        sizeOfFile, blockCount = encode._split_file(f, gv.BLOCKSIZE)

        calcK = len(blockCount)

        logger.debug("No. of Blocks: %d" %calcK)
        logger.debug("FileSize in bytes: %d" %sizeOfFile)

        calcGamma =  floor(sqrt(calcK) * (log(calcK/DEFAULT_DELTA)**2)/calcK)
        logger.debug("Gamma: %d" %calcGamma)

    return calcK, calcGamma


def checkConsistency(theirVersion, VERSION, founTT):
    """Function to check trickle message consistency RFC6206"""

    if theirVersion == VERSION:
        logger.debug("their Version:%d, our Version:%d"%(theirVersion,VERSION))
        logger.info("Consistency Detected")
        founTT.hear_consistent()

    elif theirVersion > VERSION:
        logger.debug("their Version:%d, our Version:%d"%(theirVersion,VERSION))
        logger.info("We are Behind!")
        logger.info("Inconsistency Detected")
        founTT.hear_inconsistent()

    else:
        logger.info("They are behind.. Starting Fountain")
        if founTT.can_transmit():
            global threadFount
            threadFount = threading.Thread(target=fountain, args=(gv.FILENAME, gv.BLOCKSIZE, VERSION))
            threadFount.daemon = True
            threadFount.start()
            threadFount.join()
        founTT.hear_inconsistent()
    
    print("Exiting the Check")

def fountain(FILENAME, BLOCKSIZE, VERSION):
    """Main Fountain code: will send encoded Packets upto a certain
       limit over a multicast channel
    """
    print("Sending Notification!..")

    notifier = 255
    fNotifier = pack('!H', notifier)
    fSocket.sendToSock(fNotifier, MCASTGRP)


    # Bring in the Fountain Paramaters
    K, Gamma = fountainParameters(gv.FILENAME, gv.BLOCKSIZE)

    chdir(gv.PATH)
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

            for eachBlock in encode.encoder(f, gv.BLOCKSIZE):
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

            break
            # Out of the encoder block
            

def Cognition(VERSION, founTT):
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
            checkConsistency(theirVersion, VERSION, founTT)
     

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Fountain")

    parser.add_argument('path', type = str, help = 'path to file')
    parser.add_argument('filename', type = str, help = 'name of file')
    parser.add_argument('version', type = int, help = 'version number')
    parser.add_argument('blocksize', type = int, default = 1452,help = 'mtu size < 1500 B')

    args = parser.parse_args()

    gv.PATH = args.path
    gv.FILENAME = args.filename
    VERSION = args.version
    gv.BLOCKSIZE = args.blocksize

    if not path.exists(gv.PATH):
        print("Path doesn't exist", file = sys.stderr)
        sys.exit(1)
    chdir(gv.PATH)

    if not path.isfile(gv.FILENAME):
        print("File doesn't exist", file = sys.stderr)
        sys.exit(1)
    

    # Open A MCAST socket and Bind it
    
    fSocket.bindTheSock()
    
<<<<<<< HEAD
    fountain(FILENAME, BLOCKSIZE, VERSION)
=======
    fountain(gv.FILENAME, gv.BLOCKSIZE, VERSION)
    global founTT
    founTT = trickleTimer(fSocket.sendToSock, {'message': pack('!H', VERSION), 'host': MCASTGRP, 'port': MCASTPORT})

    founTT.start()

    Cognition(VERSION, founTT)
>>>>>>> 23fc69c114b83499398e7886972876cba57b884e
