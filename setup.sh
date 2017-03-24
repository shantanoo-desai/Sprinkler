#!/bin/bash

# make folder in `this` directory
DESTDIR=$PWD
# python3 check
PY_CHECK=/usr/bin/python3
# pip3 check
PIP_CHECK=/usr/local/bin/pip3
# Use to change ownership
CURRENT_USER=$(who | awk '{print $1}')

if [[ $EUID -ne 0 ]]; then
    echo
    echo "You need root privilege to run this script."
    echo
    exit 1
fi

if [[ -x $PY_CHECK && -x $PIP_CHECK ]]; then
    echo
    echo "SETUP: python3 and pip3 already installed"
    echo
else
    echo
    echo "SETUP: Installing python3 and pip3"
    echo
    apt install python3 python3-pip

    echo
    echo "SETUP: Installing required pip modules"
    echo
    pip3 install lt-code
fi

echo
echo "SETUP: generating log folder in current directory"
echo

mkdir $DESTDIR/log
mkdir $DESTDIR/transmissions

# make dummy file for receiving Nodes
# make the argument parser point to this dummy file by default

touch $DESTDIR/transmissions/dummy.bin

# Change ownership (not root!)
chown -R $CURRENT_USER:$CURRENT_USER $DESTDIR/log $DESTDIR/transmissions

echo
echo "SETUP complete."
echo

exit 0
