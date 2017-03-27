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
Bucket Module for Sprinkler
"""

__author__ = "Shantanoo Desai"

import Sprinkler.global_variables as gv
from lt import decode
from struct import pack, unpack
from Sprinkler.fountain import CheckConsistency
from os import path
from Sprinkler.route import addRoute
import sys
import socket
import logging

# Central Logging Entity
logger = logging.getLogger("Bucket")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(path.expanduser(".") + "/log/Sprinkler.log")
handler.setLevel(logging.DEBUG)

# format for logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -'
                              '%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def open_next_file(aDecoder, template='incomingData{}.tar'):
    """
        function: open_next_file
        params: an instance of Class lt.decode.decoder
        default: template for name of incoming data

        Description:
        Function that dumps the bytes into a new file with new
        version as suffix. This function avoids overwriting
        content on the same file.
    """

    # Store upto 100 file names
    for serial in range(100):
        if not path.exists(template.format(serial)):
            # if file does not exist,
            # enter data into the new file

            with open(template.format(serial), 'wb+') as f:
                f.write(aDecoder.bytes_dump())
            break

        else:
            # if file already exists then,
            # don't write on existing files
            pass

    # Return the recent filename
    # since needs to be stored as a Global Variable for
    # FILENAME, incase if the node needs to become a fountain
    return template.format(serial)


def bucket():
    """
        function: bucket

        Description:
        This is the main receiving function where a node listens
        to the Multicast Channel for either UPDATES or VERSION CHECKS.

        Message Types:
        TrickleMessage: 2 Bytes of Version number
        Droplets: BlockSize of LT-encoder + 2 B footer for Version
    """

    logger.info("Bucket state on..")

    # instance of LT-Decoder
    decoder = decode.LtDecoder()

    # Counter
    receivedDroplets = 0

    # Consumed Block Counter
    consumedBlocks = 0

    try:
        while True:
            # Receive Data
            data, recvAddr = gv.mcastSock.receive(65535)

            if not data:
                logger.error("No data..")
                sys.exit(1)

            if len(data) == 2:

                # If data is 2 Bytes
                # this is trickleMessage
                theirVersion = unpack('!H', data)[0]
                logger.info("Version Check for %s" % recvAddr)
                # store the IP address of Trickle Neighbor
                addRoute(foun=None, neigh=recvAddr)

                CheckConsistency(theirVersion)

            elif len(data) > gv.BLOCKSIZE:
                # If length of the data more than
                # Blocksize then this is a
                # -LT-droplet
                receivedDroplets += 1

                droplet = data

                # Strip the Footer for Version
                # of Fountain
                footer = droplet[-2:]

                # fountain's version
                founVersion = unpack('!H', footer)[0]

                if gv.VERSION == founVersion:
                    # If my Version and Fountain's version
                    # is Same. Do nothing.
                    pass
                elif founVersion < gv.VERSION:
                    # If Someone else is spraying an older
                    # Found become inconsistent and make
                    # Things Right..
                    # This is particularly useful for Server
                    gv.tt.hear_inconsistent()
                else:
                    # Else Definitely this is a new OTA data
                    # feed the block to the decoder

                    # use this API (a wrapper around next())
                    lt_block = decode.block_from_bytes(droplet)

                    if decoder.consume_block(lt_block):
                        # Try creating a Bipartite Graph
                        # And Decode the file

                        # If we find the best combination
                        # Dump the data to a file for further
                        # Usage
                        logger.info("file Decoded..")

                        logger.info("writing file")

                        # This is the Block that decodes it all
                        # hence increase the consumption counter
                        consumedBlocks += 1

                        # Change to Target Folder
                        # we already are in gv.PATH through main.py

                        # Dump the Data into a new File template
                        # Automatically and assign value to the
                        # Global Filename variable
                        gv.FILENAME = open_next_file(decoder)

                        logger.debug("Total Droplets Consumed:%d"
                                     % consumedBlocks)
                        logger.debug("Total Droplets Received:%d"
                                     % receivedDroplets)

                        # Store the Fountain address in routeTable.json
                        addRoute(foun=recvAddr, neigh=None)
                        break

                    # Increase the consumption counter
                    # if this increases it means that
                    # the Droplet in the Generator
                    # wasn't the one to decode the file
                    consumedBlocks += 1

    except socket.error as sockErr:
        logger.error("Error While Listening on Socket")
        raise sockErr
        sys.exit(1)

    else:

        # Once we are updated with new Version
        # Pack the new version and send out
        # a TrickleMessage
        gv.VERSION = founVersion
        logger.debug("Version Updated: %d" % gv.VERSION)

        # Pack the newly update Version and trigger an
        # Inconsistency for faster response to the sending source
        setattr(gv.tt, 'kwargs', {'message': pack('!H', gv.VERSION)})
        gv.tt.hear_inconsistent()
