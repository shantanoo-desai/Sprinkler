#TWIN- Managing Data Dissemination

Firmware Distribution for the __TWIN__ Testbed.

## Description

Data Dissemination for __TWIN__ using __Luby Tranform Codes__ and __Trickle Algorithm__

* `fountain.py`: Implementation of a __LT-Fountain__

* `bucket.py`: Implementation of a Listening a OTA firmware Update

* `Socket.py`: Socket Wrapper with __IPv6, UDP (Multicast)__

* `trickle.py`: [RFC6206](https://tools.ietf.org/html/rfc6206) Trickle Algorithm used from [SimpleRPL](https://github.com/tcheneau/simpleRPL)

## License

Project is issued under the __GNU GPLv3__ License

## Usage

      python3 TWIN.py --help

     usage: TWIN.py [-h] [-p PATH] [-b BLOCKSIZE] [-V VERSION]

     Data Dissemination for TWIN back-channel

     optional arguments:
     -h, --help            show this help message and exit
     -p PATH, --path PATH  Path value where the incoming file should be stored.
                        This path will also be used to generate a Fountain
     -b BLOCKSIZE, --blocksize BLOCKSIZE
                        Blocksize of each LT-encoded Block. It should be less
                        than 1500 Bytes in general. Default value = 1452
     -V VERSION, --version VERSION
                        Version of the TWIN. Default is 0

