#TWIN- Managing Data Dissemination

Firmware Distribution for the __TWIN__ Testbed.

(Codes are quite often bound to change and current version: v2.0 is under Beta Phase)

## Description

Data Dissemination for __TWIN__ using __Luby Tranform Codes__ and __Trickle Algorithm__

* `fountain.py`: Implementation of a __LT-Fountain__

* `bucket.py`: Implementation of a __LT-Bucket__

* `twinSocket.py`: Socket Wrapper with __IPv6, UDP (Multicast)__

* `trickle.py`: [RFC6206](https://tools.ietf.org/html/rfc6206) Trickle Algorithm used from [SimpleRPL](https://github.com/tcheneau/simpleRPL)

## License

Project is issued under the __GNU GPLv3__ License
