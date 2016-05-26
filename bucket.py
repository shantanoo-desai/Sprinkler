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
from lt import decode

from io import BytesIO

from os import chdir

from sys import exit, stdout

from struct import pack, unpack

from twinSocket import *

from trickle import trickleTimer

import datetime, logging

logging.basicConfig(stream=stdout, level = logging.INFO)

IMIN = 0.2
IMAX = 8

def Bucket():
    """
    This Function catches the LT-encoded packets from the Fountain 
    and performs decoding based on Belief Propagation to decode the file
    while take a little more packets than the generated size of K at the Fountain  
    """
    logging.info("Starting the Receiving Mode")

    # Path on the Pi where the file needs to be stored
    # In practice, the decoded file will be stored into a folder
    # where INOTIFY-TOOLS is setup in order to trigger the uploading 
    # of the file onto the Sensor Node
    PIPATH = '/tmp/'

    # reason for specifying a specific name is the fact that
    # INOTIFY-TOOLS will trigger only if there is some change 
    # with the specified 'main.ihex' in the Target Folder
    PIFILENAME = 'trialData.tar'

    # create the LT-Decoder 
    decoder = decode.LtDecoder()

    # create a packet Counter to check if we needed more than K droplets
    dropletCounter = 0
        
    try:
        timeStamp1 = datetime.datetime.now().replace(microsecond=0)
        while True:
            """ Keep the Bucket under the Fountain! """
            droplets, FountainAddress = recvSocket.recvFromSock(65535)

            if not droplets:
                logging.error("No Droplets Received")
                break
            if len(droplets) == 2:
                theirVersion = unpack('!H', droplets)[0]
                global VERSION
                global rxtt
                if theirVersion == VERSION:
                    rxtt.hear_consistent()
                else:
                    rxtt.hear_inconsistent()
            else:

                dropletCounter += 1
                # strip the footer to check the Version and to feed
                # the Decoder the right block
                footer = droplets[-2:]
                VERSION = unpack('!H', footer)[0]                

                #Block to be fed to the LT-Decoder from the received droplet

                lt_block = next(decode.read_blocks(BytesIO(droplets)))

                # feed the block to the decoder
                if decoder.consume_block(lt_block):
                    # Return true or false if the decoding is completed
                    # if decoding is complete and file is recovered completely
                    # save the file at the location with appropriate filename
                    logging.info("File Decoded!..")
                    timeStamp2 = datetime.datetime.now().replace(microsecond=0)
                    logging.info("Droplets Consumed: %d" %dropletCounter)
                    logging.info("time taken: %s", str(timeStamp2 - timeStamp1))

                    # Change to the Path
                    chdir(PIPATH)

                    # open the file and write the decoded data bytewise
                    with open(PIFILENAME, 'wb') as f:
                        f.write(decoder.bytes_dump())
                    break
    
    
    except socket.error as e:
        logging.exception('Error: While Sending')
        recvSocket.closeSock()

    else:
        # create an updated trickMSG for the Fountain
        # ensuring the file was decoded by sending the 
        # received version number

        newVersion = pack('!H', VERSION)
        rxtt.cancel()
        
        #New Trickle Timer Instance

        try:

            rxtt = trickleTimer(recvSocket.sendToSock,{'message':newVersion, 'host':MCASTGRP, \
                                                            'port': MCASTPORT},IMIN, IMAX)
            rxtt.start()
        except socket.error as e:
            logging.exception("Error: triggering newVersion trickleTimer")
    
    Bucket()


if __name__ == "__main__":

    # Create Socket and Bind it to Multicast Port
    recvSocket = twinSocket()
    recvSocket.bindTheSock()

    # Initial Version
    myVersion = 0

    trickMSG = pack('!H', myVersion)

    # create a trickle Timer instance
    rxtt = trickleTimer(recvSocket.sendToSock,{'message':trickMSG, 'host':MCASTGRP, \
                                                        'port': MCASTPORT}, IMIN, IMAX)
    rxtt.start()


    Bucket()
