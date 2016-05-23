#!/usr/bin/python3
from lt import decode

from io import BytesIO

from os import chdir

from sys import exit

from struct import pack, unpack

from twinSocket import *

from trickle import trickleTimer

IMIN = 0.1
IMAX = 8

def Bucket():
    """
    This Function catches the LT-encoded packets from the Fountain 
    and performs decoding based on Belief Propagation to decode the file
    while take a little more packets than the generated size of K at the Fountain  
    """
    print("Starting the Receiving Mode \n")

    # Path on the Pi where the file needs to be stored
    # In practice, the decoded file will be stored into a folder
    # where INOTIFY-TOOLS is setup in order to trigger the uploading 
    # of the file onto the Sensor Node
    PIPATH = '/tmp/'

    # reason for specifying a specific name is the fact that
    # INOTIFY-TOOLS will trigger only if there is some change 
    # with the specified 'main.ihex' in the Target Folder
    PIFILENAME = 'trialData.tar'

    # Create Socket and Bind it to Multicast Port
    recvSocket = twinSocket()
    recvSocket.bindTheSock()
    recvSocket.timeout(150)

    # create the LT-Decoder 
    decoder = decode.LtDecoder()

    # create a packet Counter to check if we needed more than K droplets
    dropletCounter = 0
        
    try:
        while True:
            """ Keep the Bucket under the Fountain! """
            droplets, FountainAddress = recvSocket.recvFromSock(65535)

            if not droplets:
                print("No Droplets Received. \n")
                break
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
                print("File Decoded!..")
                print("Droplets Consumed: ", dropletCounter)

                # Change to the Path
                chdir(PIPATH)

                # open the file and write the decoded data bytewise
                with open(PIFILENAME, 'wb') as f:
                    f.write(decoder.bytes_dump())
                break
    
    # If the Socket Timeout is triggered
    except socket.error as e:
        print('timeout')
        # Create a Negative Acknowledgement to send it back to 
        # the Closed Fountain(Server)
        nackVERSION = 0
        NACK = pack('!I', nackVERSION)

        
        try:

           # create a trickle Timer instance
           rxtt = trickleTimer(recvSocket.sendToSock,{'message':NACK, 'host':FountainAddress, \
                                                        'port': MCASTPORT}, IMIN, IMAX)
           rxtt.start()
        except socket.error as e:
            print("Socket Error")
            recvSocket.closeSock()

    else:
        # create an ACKNOWLEDGEMENT for the Fountain
        # ensuring the file was decoded by sending the 
        # received version number
        #VERSION = 1
        ACK = pack('!I', VERSION)

        # Asssuming the Fountain might still be ON and the channel will
        # still be occupied and our data might not reach the fountain
        # we wait for a fixed backoff( in future this backoff will be TRICKLE based )

        try:

            rxtt = trickleTimer(recvSocket.sendToSock,{'message':ACK, 'host':FountainAddress, \
                                                            'port': MCASTPORT},IMIN, IMAX)
            rxtt.start()
        except socket.error as e:
            pass
    
    Bucket()


if __name__ == "__main__":
    Bucket()
