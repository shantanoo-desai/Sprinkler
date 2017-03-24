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

"""	Routing table Entry function
add a fountain IPv6 address or Neighbor
IPv6 address to global variable `rCache`"""

from os import chdir, path
import json
from Sprinkler.global_variables import rCache


def addRoute(foun=None, neigh=None):
    """
        Function: addRoute
        param: one fountain address, neighboring node address
        defaults: None (for both params)

        Description:
        a function to add IPv6 address of either Fountain or
        nearby neighbors and store the content into JSON format
        for future access over REST.
    """

    if foun is None or foun == "":
        # don't add anything if field
        # empty
        pass

    else:
        # if parameter exists
        # update the Dictionary
        rCache['fountain'] = foun

    if neigh is None or neigh == "":
        # don't append entry to list
        # if parameter is empty/None
        pass

    else:
        if neigh in rCache['neighbors']:
            # if the IPv6 address already
            # exists don't append it..
            pass

        else:
            rCache['neighbors'].append(neigh)

    # Save in current folder
    # Usually the path mentioned by gv.PATH
    # As in main.py we perform a chdir
    chdir(path.expanduser("."))

    with open("routeTable.json", 'w+') as rtable:
        json.dump(rCache, rtable)
