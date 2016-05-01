# TWIN: A Flexible Wireless Sensor Network Testbed

Development based on:

> Idrees Zaman, Jens Dede, and Anna Förster. 2016. Demo: TWIN Node, A Flexible Wireless Sensor Network Testbed. In Proceedings of the 2016 International Conference on Embedded Wireless Systems and Networks (EWSN '16). Junction Publishing, , USA, 237-238. 

Paper available [here](http://dl.acm.org/citation.cfm?id=2893751)


# trickleTWIN
Implementation of the Trickle Algorithm for TWIN node for __ComNets Universität Bremen__

This is an active project and any/all files or the complete repository are/is subject to changes!

Using *Multicast Addressing Scheme* `ff02::1` for disseminating code
within an Ad-Hoc network consisting of the following:

Clients:

- __Raspberry Pi 2 Model B__ with __1GB RAM__

- __LogiLink WiFi Adapter__

Server:

- __Ubuntu 14.04 LTS__ Laptop


## Usage

For general Idea:

    python main.py -h or python main.py --help

For Server (Laptop):
	
	python main.py -s /Path/to/File fileName.ihex 0x0002 
		or 
	python main.py --server /Path/to/File fileName.ihex 0x0002

For Client (RPis):

	python main.py -r
		or
	python main.py --receiver


## Structure

	-- twinSocket.py : socket class to be used 
	-- trickle.py : Implementation of Trickle Timer 
	-- message_constants.py : *pseudo-header* parameters for Version control
	-- Sender/Receiver.py: implementation of server/client respectively

### Dissemination Code

- creating a standard `.ihex` using the [Contiki-OS](https://github.com/contiki-os/contiki) for *Zolerta Z1 nodes*

### Improvements

- ~~add `VERSION` argument to be used when uploading new `.ihex` to network for version-control~~

- create a `SQL` database for all the __Link-Local IPv6 Addresses__ at the Receiver and Server

- decide on a Metric for routing and forwarding data 

    * directed diffusion routing (maybe)

### Problems

- when `.ihex` file is > ~64kB it needs to be split into chunks to be sent over __UDP__

    * Use `split` tool on Ubuntu

- dispensing this chunks with reliability over network

	* use __Fountain Coding__ (Network Coding)

### Trickle Implementation 

Taken from [simpleRPL](https://github.com/tcheneau/simpleRPL)
