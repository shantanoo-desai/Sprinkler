#!/usr/bin/python3

#   IPv6 UDP Socket Wrapper
#   for Multicast

import socket
from struct import pack, unpack
from sys import exit
from os import path
from TWIN.global_variables import MCAST_GRP, MCAST_PORT, MCAST_TTL
import logging

# Central Logging Entity
logger = logging.getLogger("Socket")
logger.setLevel(logging.ERROR)

handler = logging.FileHandler(path.expanduser("~")+"/logFiles/TWIN.log")
handler.setLevel(logging.DEBUG)

class Socket:
    """
        Class: Socket

        Description: IPv6 Multicast socket Wrapper
    """
    def __init__(self, sock = None):

        try:
            # IPv6, UDP
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

            # Multiusablity -- Optional
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            logger.info("Socket Created..")

        except socket.error as sockErr:
            logger.error("Socket Creation Failed..")
            raise sockErr
            exit()

        else:
            self.sock = sock

    def bindSock(self, host='', port=MCAST_PORT):
            """socket binding method"""

            try:
                ## UDP needs to Port
                self.sock.bind((host, port))

                # binary packing for joining group

                group_bin = socket.inet_pton(socket.AF_INET6, MCAST_GRP)

                # create membership request: value -> 0
                mreq = group_bin + pack('@I', 0)

                # join the Multicast Group w. IPv6
                self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

                # No "self message" hearing on Loopback Interface

                self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, pack('@i', 0))

                # TTL value assignment

                self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, pack('@I', MCAST_TTL))

                logger.info("Socket Binded..")

            except socket.error as sockErr:
                logger.error("Binding Failed..")
                raise sockErr
                self.sock.closeSock()
                exit()

    def send(self, message, host = MCAST_GRP, port = MCAST_PORT):
        """socket send method"""
        
        try:
            ## Send data to ff02::1 and 30001 port
            self.sock.sendto(message, (host, port))

        except socket.error as sockErr:

            logger.error("Sending Failed..")
            raise sockErr
            self.sock.closeSock()
            exit()

    def receive(self, buffvalue):
        """socket receive method"""

        try:
            ## Receive data and the Sender's Address
            incomingData, recAddr = self.sock.recvfrom(buffvalue)
            ## Only the first value of the Tuple here
            srcAddr = recAddr[0]

            return incomingData, srcAddr
        
        except socket.error as sockErr:
            logger.error("Receiving Failed..")
            raise sockErr
            exit()


    def closeSock(self):
        """Close The Socket"""

        logger.info("Socket Closed..")
        self.sock.close()
