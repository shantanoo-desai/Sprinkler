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

__author__ = "Shantanoo Desai"

import Sprinkler.global_variables as gv
import argparse
import sys
from Sprinkler.Socket import Socket
from Sprinkler.trickle import trickleTimer
from struct import pack
from Sprinkler.bucket import bucket
from os import path, chdir
import logging

# Central Logging Entity
logger = logging.getLogger("MAIN")
logger.setLevel(logging.ERROR)

handler = logging.FileHandler(path.expanduser(".") + "/log/Sprinkler.log")
handler.setLevel(logging.ERROR)

# format for logging
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def main(args):
    parser = argparse.ArgumentParser(description="Sprinkler Wireless Data\
                                    Dissemination Protocol")

    parser.add_argument("-V", "--version", type=int, default=gv.VERSION,
                        help="Version Number for Updated Data")

    parser.add_argument("-b", "--block", type=int, default=gv.BLOCKSIZE,
                        help="Encoding Block Length, keep it less than 1500B")

    parser.add_argument("-pt", "--path", type=str, default=gv.PATH,
                        help="Path to the file for Dissemination / storing\
                         Incoming file over channel.\
                         Default is current_folder/transmissions")

    parser.add_argument("-f", "--filename", type=str, default=gv.FILENAME,
                        help="Main File for Fountain. provide complete path")

    parser.add_argument("-g", "--group", type=str, default=gv.MCAST_GRP,
                        help="IPv6 Multicast Group. Default is ff02::1")

    parser.add_argument("-p", "--port", type=int, default=gv.MCAST_PORT,
                        help="port number. Default is 30001")

    args = parser.parse_args()

    gv.VERSION = args.version

    gv.BLOCKSIZE = args.block

    gv.PATH = args.path

    gv.FILENAME = args.filename

    if not path.exists(gv.PATH):
        print("Specified does not exist. use --path or -pt to add path.")
        sys.exit(1)

    if gv.FILENAME is None or gv.FILENAME == "":
        print("No File Mentioned. use --filename or -f to add a file")
        sys.exit(1)

    gv.MCAST_GRP = args.group

    gv.MCAST_PORT = args.port

    chdir(gv.PATH)
    if not path.exists(gv.FILENAME):
        print("File Does not Exist..")
        sys.exit(1)

    logger.debug("Starting with Version %d" % gv.VERSION)

    logger.info("Creating Socket..")

    gv.mcastSock = Socket()

    logger.info("Binding Socket..")
    gv.mcastSock.bindSock()

    logger.info("Configuring Trickle Timer")

    initArgs = {'message': pack('!H', gv.VERSION),
                'host': gv.MCAST_GRP,
                'port': gv.MCAST_PORT
                }

    gv.tt = trickleTimer(gv.mcastSock.send, initArgs)
    gv.tt.start()

    while True:
        bucket()
