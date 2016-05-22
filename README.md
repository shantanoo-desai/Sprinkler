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
	git clone https://github.com/anrosent/LT-Code.git
	cd LT-Code/
	python3 setup.py install
```
#### Files

1. __Fountain.py__: Server(Laptop)

    * File to be sent: a File.tar file which consists of `config.ini` and other `.ihex` files

2. __Bucket.py__ : Receiver (Raspberry Pi 2)

	* Files received from Fountain will be stored on a designated folder on Pis

3. __twinSocket.py__ : Socket Wrapper for UDP Datagrams
	
	* With `socket.timeout()`


#### Added Features (v2.1)

* Controlled dissemination of __Fountain__ in order to not flood the shared network of WiFi

* Added Feedback and Version Check for efficiency with Trickle Algorithm 

