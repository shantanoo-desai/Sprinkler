"""
    Global Variables Used Through Out the Module
"""

## Version for Trickle Algorithm
VERSION = 0

## Instance of Class trickleTimer
tt = None

## Instance of Multicast Socket

mcastSock = None

## Multicast to all ipv6-nodes

MCAST_GRP = "ff02::1"

## Multicast Port

MCAST_PORT = 30001

## TTL value for Multicasting

MCAST_TTL = 2

## Luby-Transform Block Size

BLOCKSIZE = 1452

## Filename for Encoding

FILENAME = "trialPack.tar"

## Path Variable for the Filename

PATH = "/home/testbed/hexfiles"

## Dictionary Cache for a pseudo-route table

rCache = {'fountain': '', 'neighbors':[]}
