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

#!/usr/bin/env python

from sys import argv, exit
from Server import server
from Receiver import receiver




def main():
	if len(argv) < 2:
		print "use python main.py -h or python main.py --help"
		exit(1)

	if argv[1] == '-h' or argv[1] == '--help':
		print """Script performs accordingly.\n
		USAGE: python main.py [-sr] /home/myFolder/ file.ihex  versionNumber\n
		e.g. : python main.py --server /home/user file.ihex 0x0001
		OPTIONS:
			-s or --server : to send code into network
			* Add the Path and File to be uploaded successively with version number
			  in Hexadecimal format(e.g. 0x0003)
			
			-r or --receiver : to receive code from server
		"""
		exit(1)


	elif argv[1] == '-s' or argv[1] == '--server':
		if (len(argv) < 3):
			print "Insert Path of the File and the File to be Uploaded with code version. Use -h or --help" \
			" for USAGE"	
			exit(1)
		PATH = argv[2]
		FILENAME = argv[3]
		versionNumber = argv[4]
		server(PATH, FILENAME, versionNumber)

	elif argv[1] == '-r' or argv[1] == '--receiver':
		receiver()

	





if __name__ == "__main__":
	main()
