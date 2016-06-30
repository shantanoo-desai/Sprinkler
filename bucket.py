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

from struct import pack, unpack

from twinSocket import *

from trickle import trickleTimer

import datetime, logging, time, threading

from fountain import fountain, checkConsistency

import global_variables as gv


recvSocket = twinSocket()


# Logging Configuration
logger = logging.getLogger("Bucket")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('./logFiles/bucket.log')
handler.setLevel(logging.DEBUG)

# format for logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



def Bucket(version):
    """Receive Droplets from the Fountain and decode the File.
        Trigger Trickle Timer for Consistency Check  
    """
    logger.info("Starting Cognition State")
    
    # create the LT-Decoder 
    decoder = decode.LtDecoder()

    # create a packet Counter to check if we needed more than K droplets
    dropletCounter = 0
        
    try:
        
        while True:
            """ Keep the Bucket under the Fountain! """
            droplets, FountainAddress = recvSocket.recvFromSock(65536)

            if not droplets:
                logger.error("No Droplets Received")
                break

            # Since the Datapackets may Vary in size! (Trickle Messages or
            # Fountain Droplets)

            # if Trickle Messages 
            if len(droplets) == 2:

                theirVersion = unpack('!H', droplets)[0]    

                # their Version
                logger.info("Version check for %s"%FountainAddress)
                global buckTT
                checkConsistency(theirVersion, version, buckTT)

            # If Droplets..
            elif len(droplets) > 1000:
                
                dropletCounter += 1

                # strip the footer to check the Version and to feed
                # the Decoder the right block
                footer = droplets[-2:]
                founVERSION = unpack('!H', footer)[0]

                # if myVersion and founVersion are same try to do nothing since we already have the file
                if version == founVERSION:
                    try:
                        pass
                    except:
                        pass
                else:
                    #Block to be fed to the LT-Decoder from the received droplet
                    
                    # new data and new version

                    lt_block = next(decode.read_blocks(BytesIO(droplets)))

                    # feed the block to the decoder
                    if decoder.consume_block(lt_block):
                        # Return true or false if the decoding is completed
                        # if decoding is complete and file is recovered completely
                        # save the file at the location with appropriate filename
                        logger.info("File Decoded!..")
                        logger.debug("Droplets Consumed: %d" %dropletCounter)
                        logger.info("Source: %s"%FountainAddress)
                        gv.fountCache.append(FountainAddress)

                        # Change to the Path
                        chdir(gv.PATH)

                        # open the file and write the decoded data bytewise
                        with open(gv.FILENAME, 'wb') as f:
                            f.write(decoder.bytes_dump())

                        break

                
    
    except socket.error as e:
        logger.exception('Error: While Sending Socket Error')
        recvSocket.closeSock()

    else:
        # create an updated trickMSG for the Fountain
        # ensuring the file was decoded by sending the 
        # received version number
        global myVersion
        myVersion = founVERSION
        version = myVersion
        print("myVersion now %d"%version)
        Version = pack('!H', version)
        buckTT.cancel()
        
        #New Trickle Timer Instance

        try:
            buckTT = trickleTimer(recvSocket.sendToSock, {'message':Version, 'host':MCASTGRP, 'port': MCASTPORT})
            buckTT.start()

        except socket.error as e:
            logger.error("Error while Trickle Timer set")
    


if __name__ == "__main__":

    # Create Socket and Bind it to Multicast Port
    
    recvSocket.bindTheSock()

    # Path on the Pi where the file needs to be stored
    # In practice, the decoded file will be stored into a folder
    # where INOTIFY-TOOLS is setup in order to trigger the uploading 
    # of the file on Sensor

    gv.PATH = '/tmp/'
    chdir(gv.PATH)

    # file Name
    gv.FILENAME = 'incomingData.tar'

    # Initial Version
    global myVersion
    myVersion = 0


    global buckTT
    
    buckTT = trickleTimer(recvSocket.sendToSock,{'message':pack('!H', myVersion), 'host':MCASTGRP, 'port': MCASTPORT})
    buckTT.start()


    while True:
        Bucket(myVersion)