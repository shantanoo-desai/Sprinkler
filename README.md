# Sprinkler

An efficient IPv6 Multicast Protocol for distributing data over a wireless network.

It uses:

1. [__Luby-Transform Codes__](https://en.wikipedia.org/wiki/Luby_transform_code)
2. [__Trickle Algorithm__](https://tools.ietf.org/html/rfc6206)

## Usability over

* __802.11 WLAN ad-hoc networks with Raspberry Pis and GNU/Linux computers__

## Usage

__Case__:


    python3 Sprinkler.py
    --version 1 --path /path/to/dir/
    --filename file_to_send --group ff32::2
    --port 30002

will distribute the file `/path/to/dir/file_to_send` over the wireless ad-hoc network Nodes
which are running the same code but will lower `version` number (for instance __0__).
 The `/path/to/dir` will also store all new incoming files.

General:
```
usage: Sprinkler.py [-h] [-V VERSION] [-b BLOCK] [-pt PATH] [-f FILENAME]
                [-g GROUP] [-p PORT]

Sprinkler Wireless Data Dissemination Protocol

optional arguments:
-h, --help            show this help message and exit
-V VERSION, --version VERSION
                    Version Number for Updated Data
-b BLOCK, --block BLOCK
                    Encoding Block Length, keep it less than 1500B
-pt PATH, --path PATH
                    Path to the file for Dissemination / storing Incoming
                    file over channel. Default is
                    current_folder/transmissions
-f FILENAME, --filename FILENAME
                    Main File for Fountain. provide complete path
-g GROUP, --group GROUP
                    IPv6 Multicast Group. Default is ff02::1
-p PORT, --port PORT  port number. Default is 30001

```

### Setup

    sudo ./setup.sh

This file will:

* Check for `python3` and `pip3`

* install the `lt-code` pip module

* make necessary folders for the API and relevant dummy files for default operation

* creates `routeTable.json` for storing information of nearby neighbors and source of information `fountain`

## Application

* Currently being used in [TWIN Testbed](https://github.com/ComNets-Bremen/TWIN) at the [Sustainable Communication Networks, University of Bremen, Germany](http://comnets.uni-bremen.de) to distribute firmware over __802.11 WLAN back-channel__

## Dependencies

It uses [LT-Code Github Repository by Anson Rosenthal](https://github.com/anrosent/lt-code)

install `pip3` module first using:

    sudo pip3 install lt-code

## References

[Complete Report of the Protocol at ResearchGate](http://dx.doi.org/10.13140/RG.2.2.32561.99687)

### License

published under __GNU Public License v3 (GPLv3)__
