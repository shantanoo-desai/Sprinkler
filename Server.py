#!/usr/bin/python3
from sys import argv, exit
import os, time
from twinSocket import *
from struct import pack
from lt import encode


stdBlockSize = 1470

def server(PATH, FILENAME):

    print("Starting Server Mode\n")
    
    #------------PATH CHECK ------------------
    pathFLAG = os.path.exists(PATH)

    if not pathFLAG:
        print("Mentioned path does not exist. Check Again\n")
        exit(1)
    else:
        print("Path exists.. checking file..\n")
        # change into the given path
        os.chdir(PATH)

    #------------ FILE CHECK -----------------
    fileFlag = os.path.isfile(FILENAME)

    if not fileFlag:
        print("Mentioned File does not exist. Check Again\n")
        exit(1)
    else:
        print("File exists..\n")

    # Intel HEXCODE (.ihex) used here
    
    with open(FILENAME, 'rb') as f:

        sizeFile, Blocks = encode._split_file(f, stdBlockSize)
        print("size of file is (Bytes): ", sizeFile)
        print ("number of Blocks: ", len(Blocks))
        packetCounter = 0

    # -------------- Socket for Sending 
    with open(FILENAME, 'rb') as f:
        servSocket = twinSocket()

        while True:
            print("Starting Fountain \n")
            for each in encode.encoder(f, stdBlockSize):
                try:
                    servSocket.sendToSock(each, MCASTGRP)
                    packetCounter += 1
                    if packetCounter not in range(3*len(Blocks)):
                        print("Packets Sent: ", packetCounter)
                        print("Closing Fountain")
                        break
                except (socket.error,OSError) as e:
                    print("Error in Socket Sending procedure..")
                    exit(1)
            break

    servSocket.closeSock()

if __name__ == '__main__':
    server(PATH='/home/testbed/hexfiles', FILENAME='tmpimage.ihex')
    #server(PATH='/tmp/', FILENAME='myTry.tar.gz')