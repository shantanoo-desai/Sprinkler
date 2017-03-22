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

"""
    Global Variables Used Through Out the Module
"""

# Version for Trickle Algorithm
VERSION = 0

# Instance of Class trickleTimer
tt = None

# Instance of Multicast Socket

mcastSock = None

# Multicast to all ipv6-nodes

MCAST_GRP = "ff02::1"

# Multicast Port

MCAST_PORT = 30001

# TTL value for Multicasting

MCAST_TTL = 2

# Luby-Transform Block Size

BLOCKSIZE = 1450

# Filename for Encoding

FILENAME = "./log/dummy.bin"

# Dictionary Cache for a pseudo-route table

rCache = {'fountain': '', 'neighbors': []}
