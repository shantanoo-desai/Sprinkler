import socket
from struct import pack, unpack
from sys import exit

# Link-Local group
MCASTGRP = 'ff02::1'
# port number
MCASTPORT = 30001
# host (is empty)
#MCASTHOST = ''
# TTL for Multicasting (default value = 1)
# Increase value to increase reach
MTTL = 1

class twinSocket(object):
    """Class for Socket Creation and Binding and also Sending and Receiving data.."""
    def __init__(self, sock = None):
        """Create a socket"""
                    
        try:
            # creating a socket
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            # this is Optional --> multiuse of the Socket
            #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("SOCKET CREATED....")

        except socket.error as e:
            print("SOCKET CREATION FAILED.. ERROR CODE: " + str(e[0]) + "Message: " + e[1])
            exit()

        else:
            # assign the socket if already created
            self.sock = sock

    def bindTheSock(self, host = '', port = MCASTPORT):
        """Bind the Socket for Multicasting"""
        
        try:
            self.sock.bind((host, port))

                # Pack binary for joining the group
            group_bin = socket.inet_pton(socket.AF_INET6, MCASTGRP)
                # create a membership request by packing 0
            mreq = group_bin + pack('@I', 0)
                # join the Multicast Group
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
                # do not hear "self messages" on Loopback interface
                # pack zero to stop loopback
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, pack('@i', 0))
                # to increase reach of the LL multicasting --> increase MTTL value
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, pack('@I', MTTL))
            print("SOCKET BINDED....")

        except socket.error as e:
            print("SOCKET BINDING FAILED.. ERROR CODE: " + str(e[0]) + "Message: " + e[1])
            exit()

    def sendToSock(self, message, host = MCASTGRP, port = MCASTPORT):
        """Class Function to send data over the Socket.."""
        try:
            self.sock.sendto(message, (host, port))
        except socket.error as e:
            print("SENDING FAILED.. ERROR CODE: " + str(e[0]) + "Message: " + e[1])
            exit()

    def recvFromSock(self, buffvalue):
        """Class Function to receive data over the Socket.."""
        # we receive information in the form of tuple with tuple[0] = dataRec and tuple[1] = tuple of sender
        gotSomething, whereFrom = self.sock.recvfrom(buffvalue)
        source = whereFrom[0]

        # return a Tuple in the same form but more clearly: Data, LL-IPv6-Address 
        return gotSomething, source

    def closeSock(self):
        print("CLOSING SOCKET..")
        self.sock.close()