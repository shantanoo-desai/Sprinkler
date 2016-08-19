#!/usr/bin/python3

#	Routing table Entry function
#	add a fountain IPv6 address or Neighbor
#	IPv6 address to global variable `rCache`

from os import chdir, path
import json
from TWIN.global_variables import rCache

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
        ## don't add anything if field
        ## empty
        pass

    else:
        ## if parameter exists
        ## update the Dictionary
        rCache['fountain'] = foun

    if neigh is None or neigh == "":
        ## don't append entry to list
        ## if parameter is empty/None
        pass

    else:
        if neigh in rCache['neighbors']:
            ## if the IPv6 address already
            ## exists don't append it..
            pass

        else:
            rCache['neighbors'].append(neigh)

    # Save in /home/ folder
    chdir(path.expanduser("~"))

    with open("routeTable.json", 'w+') as rtable:
        json.dump(rCache, rtable)
