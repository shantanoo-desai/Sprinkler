"""
 TWIN Node - A Flexible Wireless Sensor Network Testbed
*
* Copyright (C) 2016, Communication Networks, University of Bremen, Germany
*
* This program is free software; you can redistribute it and/or modify it
* under the terms of the GNU General Public License as published by the
* Free Software Foundation; version 3 of the License.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
* or FITNESS FOR A PARTICULAR PURPOSE.
* See the GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along
* with this program; if not, see <http://www.gnu.org/licenses/>
*
* This file is part of TWIN project
"""


"""
HEADER CREATION FOR VERSION CHECK
 _______________________
|MESSAGEVERSION |DATALEN|
|_______________|_______|
Further addition in the future

"""
# For server keep this 0x0001
# for receivers keep this 0x0000
# and let turn to 0x0001
MSGVERSION = 0x0001

DATALEN = 0
