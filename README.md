#TWIN- Managing Data Dissemination

Firmware Distribution for the __TWIN__ Testbed.

## Description

Data Dissemination for __TWIN__ using __Luby Tranform Codes__ and __Trickle Algorithm__

* `fountain.py`: Implementation of a __LT-Fountain__

* `bucket.py`: Implementation of a Listening a OTA firmware Update

* `Socket.py`: Socket Wrapper with __IPv6, UDP (Multicast)__

* `trickle.py`: [RFC6206](https://tools.ietf.org/html/rfc6206) Trickle Algorithm used from [SimpleRPL](https://github.com/tcheneau/simpleRPL)

* `global_variables.py`: Variables used throughout the Module with initial Default values.

## License

Project is issued under the __GNU GPLv3__ License

## Usage

		python3 TWIN.py --help

		usage: TWIN.py [-h] [-V VERSION] [-b BLOCK] [-p PATH] [-f FILENAME]

		Data Dissemination in TWIN Back-Channel

		optional arguments:
		  -h, --help            show this help message and exit
		  -V VERSION, --version VERSION
		                        Version Number
		  -b BLOCK, --block BLOCK
		                        Encoding Block Length
		  -p PATH, --path PATH  Target Folder for Filename
		  -f FILENAME, --filename FILENAME
		                        Main File for Fountain