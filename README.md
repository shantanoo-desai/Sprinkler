### Fountain Coding Practical Application

#### Testing Devices

* Laptop with __Ubuntu 14.04 LTS__

* Raspberry Pi-2 Model B

* Using IPv6 Multicast Addressing `ff02::1`

* Code in __Python-3.x__

#### Requirements

* Use `python3-pip` on Ubuntu-14.04 LTS for installing the __PyPi__ module of *LT-Codes* by Anson Rosenthal
```
    sudo apt-get install python3-pip
    pip3 install lt-code
```
* Since no __Python-3.4__ available for Raspberry Pi-2 (still in Beta)
```
	git clone https://github.com/anrosent/LT-Codes.git
	cd LT-Codes/
	python3 setup.py install
```
#### Files

1. __Server.py__: Server(Laptop)

    * File to be sent: __intel Hex File__ (`.ihex`)

2. __Receiver.py__ : Receiver (Raspberry Pi 2)

3. __twinSocket.py__ : Socket Wrapper for UDP Datagrams


#### Added Features (v2.0)

* Controlled dissemination of __Fountain__ in order to not flood the shared network of WiFi

* Added Feedback and Version Check for efficiency 


#### Problems

~~Can't figure out how to decode data at Pi. Problem arises at `stream.read(12)` since the __bytes__ cannot be *read*~~

Found fix with __Pull Request__ from @anrosent

#### Next Milestone

> Integrate Trickle Algorithm
