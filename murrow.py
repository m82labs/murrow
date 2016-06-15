#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from ui import MurrowFeedReader
from multiprocessing import Process
from db import initdb
from db.murrow_data import background_updater


if __name__ == '__main__':
    if sys.version_info[0] < 3:
        print("Murrow Requires Python3!")
        sys.exit(1)

    initdb()
    print("Starting the background updater...")
    updater = Process(target = background_updater, args = (15,))
    updater.start()
    app = MurrowFeedReader()
    app.run()
    updater.terminate()
    print("Exiting...")
