#!/usr/bin/env python
import npyscreen
import db.murrow_data as md
from db import session_scope


class FeedList(npyscreen.MultiLineAction):
    def __init__(self, *args, **kwargs):
        super(FeedList, self).__init__(*args, **kwargs)
        self.add_handlers({
            "^F": self.when_display_feeds()
        })

    def when_display_feeds(self):
        print "test"
        self.parent.update_feeds()


class MainDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = FeedList

    def update_feeds(self):
        with session_scope() as session:
            feeds = md.get_feed(session)

        self.wMain.values = [f.title for f in feeds]
        self.wMain.display()


class MurrowFeedReader(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainDisplay)
