#!/usr/bin/python3
# import Sprinkler
from time import sleep
from threading import Thread
import os


def test():
    os.system("python3 Sprinkler.py")


if __name__ == "__main__":

    t = Thread(target=test)

    t.daemon = True

    t.start()

    sleep(30)
