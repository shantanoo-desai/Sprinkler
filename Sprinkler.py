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

"""Main Script to call the Sprinkler Module
"""

__author__ = "Shantanoo Desai"
__copyright__ = "Copyright (C) 2017, Shantanoo Desai"
__license__ = "GPL"
__version__ = "3"
__email__ = "shantanoo.desai@gmail.com"

import sys
from Sprinkler.main import main


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Stop.")
        sys.exit(0)
