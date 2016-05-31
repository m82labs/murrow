#!/usr/bin/env python
import npyscreen
import curses.ascii
import time
import db.murrow_data as md
from db import session_scope


class CommandProcessor(npyscreen.ActionControllerSimple):
    """
    Default command processor
    """
    def create(self):
        self.add_action('^/feeds.*', self.parent.c_show_feeds, False)
        self.add_action('^/add.*', self.parent.c_add_feed, False)


class FeedList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(FeedList, self).__init__(*args, **keywords)

    def display_value(self, vl):
        """
        Override the default display with a unicode variant.
        :param vl:
        :return:
        """
        try:
            r_str = "{0:3} | ".format(vl.id) + vl.title
            return unicode(r_str)
        except ReferenceError:
            return '****REFERENCE ERROR****'

    def actionHighlighted(self, choice, key_press):
        self.parent.parentApp.getForm('FEEDITEMLIST').value = choice
        self.parent.parentApp.switchForm('FEEDITEMLIST')


class FeedListDisplay(npyscreen.FormMuttActive):
    MAIN_WIDGET_CLASS = FeedList
    ACTION_CONTROLLER = CommandProcessor
    DATA_CONTROLER = md.Feed

    def __init__(self, *args, **keywords):
        super(FeedListDisplay, self).__init__(*args, **keywords)
        self.add_handlers({
            "q": self.parentApp.exit_app,
            "a": self.c_add_feed_form
        })
        # --========= Set title and shortcut help bar text =========-- #
        self.wStatus1.value = "[Murrow] Feeds "
        self.wStatus2.value = "a:Add   d:Delete   q:Quit "
        self.c_show_feeds()

    def beforeEditing(self, *args, **keywords):
        self.c_show_feeds()

    def c_show_feeds(self, *args, **keywords):
        with session_scope() as session:
            feeds = md.get_feed(session)

        self.wMain.values = [f for f in feeds]
        self.wMain.display()

    def c_add_feed(self, command_line, widget_proxy, live):
        npyscreen.notify("Adding new feed...", title = 'Status')
        with session_scope() as session:
            msg = md.add_feed(session, command_line)

        self.c_show_feeds()

    def c_add_feed_form(self, *args, **keywords):
        self.parentApp.switchForm('FEEDADD')


class FeedItemList(npyscreen.MultiLineAction):
    def __init__ (self, *args, **keywords):
        super(FeedItemList, self).__init__(*args, **keywords)
        self.add_handlers({
            "q": self.go_back,
            "u": self.c_update_feed
        })

    def display_value (self, vl):
        """
        Override the default display with a unicode variant.
        :param vl:
        :return:
        """
        try:
            return unicode("{} |{}| {}").format(
                vl.date_published,
                ' ' if vl.is_read else 'U',
                vl.title
            )
        except ReferenceError:
            return '****REFERENCE ERROR****'

    def actionHighlighted (self, choice, key_press):
        self.parent.parentApp.getForm('FEEDITEM').value = choice
        self.parent.parentApp.switchForm('FEEDITEM')

    def c_update_feed (self, *args, **keywords):
        npyscreen.notify("Retrieving new feed items...", title = 'Status')
        with session_scope() as session:
            feed = md.get_feed(session, self.parent.value.id).one()
            item_count = feed.update_items(session)
        if item_count > 0:
            npyscreen.notify("Feed updated", title = 'Status')
        else:
            npyscreen.notify("No new, or updated, items", title = 'Status')
        time.sleep(0.5)
        self.parent.c_show_feed_items()

    def go_back (self, *args, **keywords):
        self.parent.wStatus1.value = ""
        self.parent.wStatus1.display()
        self.parent.parentApp.switchFormPrevious()


class FeedItemListDisplay(npyscreen.FormMuttActive):
    MAIN_WIDGET_CLASS = FeedItemList
    # ACTION_CONTROLLER = CommandProcessor
    DATA_CONTROLER = md.FeedItem

    def __init__(self, *args, **keywords):
        super(FeedItemListDisplay, self).__init__(*args, **keywords)
        # --========= Set shortcut help bar text =========-- #
        self.wStatus2.value = "q:Go Back   u:Update Feed "

    def beforeEditing(self):
        feed = self.value
        # --========= Set title bar text =========-- #
        self.wStatus1.value = unicode("[Murrow] {} {} ").format(
            feed.title,
            '-' + feed.description if len(feed.description) > 0 else ''
        )
        self.c_show_feed_items()

    def c_show_feed_items(self):
        feed = self.value
        with session_scope() as session:
            feeditems = feed.get_items(session)

        self.wMain.values = [i for i in feeditems]
        self.wMain.display()


class MyPager(npyscreen.Pager):
    def __init__ (self, *args, **keywords):
        super(MyPager, self).__init__(*args, **keywords)

    def display_value(self,vl):
        return unicode(vl)


class FeedItemSingleDisplay(npyscreen.ActionForm):
    OK_BUTTON_TEXT = 'Done'
    DATA_CONTROLER = md.FeedItem

    def __init__ (self, *args, **keywords):
        super(FeedItemSingleDisplay, self).__init__( *args, **keywords)
        self.add_handlers({
            "q": self.on_ok,
            "w": self.on_cancel,
            "?": self.get_help
        })

    def create(self):
        self.title = self.add(npyscreen.FixedText, name = "Title")
        self.content = self.add(MyPager, wrap = True, autowrap = True, name = "Content")

    def beforeEditing(self):
        fi = self.value
        self.title.value = "## " + fi.title.upper() + " ##"
        self.content.values = fi.content.split('\n')

    def get_help(self, *args, **keywords):
        npyscreen.notify_confirm(title="Help", message = "q: Quit\nw: Leave unread")

    def on_ok(self, * args, **keywords):
        with session_scope() as session:
            md.mark_as_read(session, self.value.feed_id, self.value.url)
        self.parentApp.switchFormPrevious()

    def on_cancel(self, *args, **keywords):
        self.parentApp.switchFormPrevious()


class FeedAdd(npyscreen.ActionForm):
    OK_BUTTON_TEXT = "Add"

    def create(self):
        self.feedurl = self.add(npyscreen.TitleText, name="Feed Url")

    def on_ok(self, *args, **keywords):
        npyscreen.notify("Adding new feed...")
        with session_scope() as session:
            md.add_feed(session, self.feedurl.value)
        self.parentApp.switchFormPrevious()

    def on_cancel(self, *args, **keywords):
        self.parentApp.switchFormPrevious()


class MurrowFeedReader(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", FeedListDisplay)
        self.addForm("FEEDITEMLIST", FeedItemListDisplay)
        self.addForm("FEEDITEM", FeedItemSingleDisplay)
        self.addForm("FEEDADD", FeedAdd)

    def exit_app(self, *args, **keywords):
        self.switchForm(None)