#!/usr/bin/python3

# Sprinkler - Data Dissemination Protocol for Wireless Networks
# Copyright (C) 2017  Shantanoo Desai
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is a part of Sprinkler

"""
Fountain Module for Sprinkler
"""

__author__ = "Shantanoo Desai"

from lt import encode
from lt.sampler import DEFAULT_DELTA
from struct import pack
from math import log, sqrt
import Sprinkler.global_variables as gv
import datetime
import socket
from os import chdir, path
import logging

# Central Logging Entity
logger = logging.getLogger("Fountain")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(path.expanduser(".") + "/log/Sprinkler.log")
handler.setLevel(logging.DEBUG)

# format for logging
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def addFooter(encodedBlock, version):
    """
        Function: addFooter
        params:
        encodedBlock:from the LT-Encoder
        version: 2 Byte value of version to be pack as Footer

        return type: Packet of (Blocksize=1452B + 2B_footer)

        Description:
        Packing a 2 Byte recent version of the Node to
        and LT-encoded Block
    """

    # Concatenate 2B of Version to the Block
    packedData = encodedBlock + pack('!H', version)
    return packedData


def FounParameters(fname=gv.FILENAME, bsize=gv.BLOCKSIZE):
    """
        Function: FounParameters
        params:
        fname = filename which needs to be LT-encoded
        bsize = Blocksize of each Encoded LT-Block
        default: Global FileName and BlockSize Values

        return type: tuple Values of K and Gamma

        Description:
        Function give out the 'Controlling Parameters' of the Fountain
        K = Number of Blocks generated
        Gamma = Bound of how many more packets would be needed to decode
            the file Completely.
    """

    # Change to Target Path
    chdir(gv.PATH)

    # Open the Target File
    with open(fname, 'rb') as f:
        fileSize, blockCount = encode._split_file(f, bsize)

    # Determine Value of K
    calculated_K = len(blockCount)
    logger.debug("FileSize in KB:%0.2f" % (fileSize / 1000))
    logger.debug("No. of Blocks:%d" % calculated_K)

    # Determine Value of Gamma
    calculated_Gamma =\
        (
            sqrt(calculated_K) *
            (log(calculated_K / DEFAULT_DELTA))**2 / calculated_K
        )
    logger.debug("Value of Gamma: %f" % calculated_Gamma)

    return calculated_K, calculated_Gamma


def CheckConsistency(incomingVersion):
    """
        Function: CheckConsistency
        params:
        incomingVersion: Incoming 2 Byte version from a neighboring node
        on the Multicast Channel

        Description:
        Version Check for Consistency based on Trickle Algorithm (RFC6206)
        If Versions are same => Hear Consistent
        If We are behind => Trigger Inconsistency and wait for Update
        If We are ahead => Start a Fountain of the Update
    """

    logger.debug("theirs: %d, ours:%d" % (incomingVersion, gv.VERSION))

    if gv.VERSION == incomingVersion:
        # If values are same
        # Consistent
        if gv.tt.c > gv.tt.k or gv.tt.function.__name__ == 'fountain':

            # If we are in supressed transmission state
            # c >= k an if the timer resets
            # chances are we might spray an unecessary fountain once
            # if that is the case: rather send a TrickleMessage
            setattr(gv.tt, 'function', gv.mcastSock.send)
            setattr(gv.tt, 'kwargs', {'message': pack('!H', gv.VERSION),
                                      'host': gv.MCAST_GRP,
                                      'port': gv.MCAST_PORT}
                    )
        logger.info("Consistent")
        gv.tt.hear_consistent()
    else:

        if gv.VERSION < incomingVersion:
            # If we are Behind
            # - Inconsistent message and anticipate
            # Update
            logger.info("Lower")
            gv.tt.hear_inconsistent()

        else:
            # If we are ahead
            # - start a Fountain at on the TrickleTimer Instance
            # - This is still an Inconsistency
            logger.info("We are higher, Setup Fountain")

            # set attributes to the already defined Global trickleTimer
            # instance called tt

            # Set the function
            setattr(gv.tt, 'function', fountain)
            # Set the Arguments
            setattr(gv.tt, 'kwargs', {'fname': gv.FILENAME,
                                      'bsize': gv.BLOCKSIZE, 'ver': gv.VERSION}
                    )

            gv.tt.hear_inconsistent()

    # Pretty much done with the check
    logger.info("Exiting Consistency Check")


def fountain(fname=gv.FILENAME, bsize=gv.BLOCKSIZE, ver=gv.VERSION):
    """
        Function: fountain
        params:
        fname: Filename which will be the LT-encoded
        bsize: Blocksize of each encoded Block
        ver: VERSION which will be contatenated as a footer
            for each LT-encoded Block
        default: all Global values

        Description:
        1. Determine the K, Gamma values of the target File
        2. Open the File and perform the LT-Encoded Block
        3. Add 2B Version Footer at end of each Encoded Block
        4. Send the Droplet to Multicast Channel
        5. Check for the Sending Limit => (1+Gamma)*K
        6. If Limit is reached Stop the Fountain
    """

    # Step 1:
    k, g = FounParameters(fname, bsize)

    # Step 2:
    chdir(gv.PATH)

    with open(fname, 'rb') as f:

        # Limit Check Counter
        packetCounter = 0

        while True:
            # Time Stamp @ beginning
            timeStamp1 = datetime.datetime.now().replace(microsecond=0)

            logger.info("Start Fountain")

            # Encode Each Block
            for eachBlock in encode.encoder(f, bsize):

                # Step 3:
                droplet = addFooter(eachBlock, gv.VERSION)

                try:
                    # Step 4:
                    # Send to all the Multicast Members.
                    gv.mcastSock.send(droplet, gv.MCAST_GRP)
                    packetCounter += 1

                    # Step 5:
                    if (packetCounter >= (1 + round(g, 1)) * k):

                        # Time Stamp @ End
                        timeStamp2 = datetime.datetime.now().replace(
                            microsecond=0)
                        # Some stats
                        logger.debug("Droplets sent %d" % packetCounter)
                        logger.debug("time needed %s s"
                                     % (timeStamp2 - timeStamp1))

                        # Step 6:
                        logger.info("Closing Fountain")
                        break

                except socket.error as sockErr:
                    raise sockErr
                    logger.error("Error in Socket while sending via Fountain")
            break
