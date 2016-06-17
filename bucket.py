#!/usr/bin/python3

from lt import decode

from io import BytesIO

from os import chdir

from struct import pack, unpack

from twinSocket import *

from trickle import trickleTimer

import datetime, logging, time

# Optimized Trickle Parameters for Single Hop setup
IMIN = 10
IMAX = 9

# Logging Details
logger = logging.getLogger("Bucket")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('bucket.log')
handler.setLevel(logging.ERROR)

#logging format -> Time will be irrelevant since in AdHoc no NTP Server
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def checkConsistency(theirVersion, myVersion, buckTT):
    """Function to check trickle message consistency RF6206"""

    if theirVersion == myVersion:
    
        logger.debug("their Version:%d our Version:%d"%(theirVersion, myVersion))
        logger.info("Consistency Detected")
        buckTT.hear_consistent()
    
    elif theirVersion > myVersion:

        # if someone has a newer version!! 
        logger.info("Our Version Lagging. Cognition State on!")
        buckTT.hear_inconsistent()
        
    elif myVersion > theirVersion:
    
        # if I am better at the Version of Data

        logger.info("Our Version is Higher. Start Fountain")
        ### START FOUNTAIN HERE



def Bucket(myVersion):
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

                decider = unpack('!H', droplets)[0]
                if decider == 255:
                    # if notifier message do nothing but listen
                    logger.info("Received a Notifier Message")

                elif decider != 255:
                    # if not Notifier Message then it must be their Version
                    theirVersion = decider
                    checkConsistency(theirVersion, myVersion, buckTT)

            # If Droplets..
            elif len(droplets) > 1000:
                
                dropletCounter += 1

                # strip the footer to check the Version and to feed
                # the Decoder the right block
                footer = droplets[-2:]
                founVERSION = unpack('!H', footer)[0]

                # if myVersion and founVersion are same try to do nothing since we already have the file
                if myVersion == founVERSION:
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

                        # Change to the Path
                        chdir(PIPATH)

                        # open the file and write the decoded data bytewise
                        with open(PIFILENAME, 'wb') as f:
                            f.write(decoder.bytes_dump())

                        break

                
    
    except socket.error as e:
        logger.exception('Error: While Sending Socket Error')
        recvSocket.closeSock()

    else:
        # create an updated trickMSG for the Fountain
        # ensuring the file was decoded by sending the 
        # received version number
        myVersion = founVERSION
        print("myVersion now %d"%myVersion)
        Version = pack('!H', myVersion)
        buckTT.cancel()
        
        #New Trickle Timer Instance

        try:

            rxtt = trickleTimer(recvSocket.sendToSock,{'message':Version, 'host':MCASTGRP, 'port': MCASTPORT},IMIN, IMAX)
            rxtt.start()

        except socket.error as e:
            logger.exception("Error: triggering newVersion trickleTimer")
    
    Bucket(myVersion)


if __name__ == "__main__":

    # Create Socket and Bind it to Multicast Port
    recvSocket = twinSocket()
    recvSocket.bindTheSock()

    # Path on the Pi where the file needs to be stored
    # In practice, the decoded file will be stored into a folder
    # where INOTIFY-TOOLS is setup in order to trigger the uploading 
    # of the file on Sensor
    global PIPATH
    PIPATH = '/tmp/'

    # file Name
    global PIFILENAME
    PIFILENAME = 'incomingData.tar'

    # Initial Version
    myVersion = 0

    trickMSG = pack('!H', myVersion)

    # create a trickle Timer instance
    buckTT = trickleTimer(recvSocket.sendToSock,{'message':trickMSG, 'host':MCASTGRP, 'port': MCASTPORT}, IMIN, IMAX)
    
    buckTT.start()

    Bucket(myVersion)
