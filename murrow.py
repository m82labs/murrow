#!/usr/bin/env python
from ui import MurrowFeedReader
from multiprocessing import Process
from db import initdb,session_scope
from db.murrow_data import background_updater

if __name__ == '__main__':
    initdb()
    updater = Process(target = background_updater, args = (15,))
    updater.start()
    app = MurrowFeedReader()
    app.run()
    print "Exiting..."
