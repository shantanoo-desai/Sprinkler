### Fountain Coding Practical Application

#### Testing Devices

* Laptop with __Ubuntu 14.04 LTS__

* Raspberry Pi-2 Model B

* Using IPv6 Multicast Addressing `ff02::1`

* Code in __Python-3.x__

#### Requirements

Use `python3-pip` for installing the __PyPi__ module of *LT-Codes* by Anson Rosenthal

    sudo apt-get install python3-pip
	pip3 install lt-code

#### Files

1. __Server.py__: Server(Laptop)

    * File to be sent: __intel Hex File__ (`.ihex`)

2. __Receiver.py__ : Receiver (Raspberry Pi:2)

3. __twinSocket.py__ : Socket Wrapper for UDP Datagrams


