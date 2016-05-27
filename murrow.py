#!/usr/bin/env python
from ui import MurrowFeedReader
from db import initdb

if __name__ == '__main__':
    initdb()
    app = MurrowFeedReader()
    app.run()
    print "Exiting..."
