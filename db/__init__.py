import os, sys
import sqlite3

db_path = os.path.join(os.path.expanduser('~'), '.murrow', 'murrow.db')


class session_scope():
    """
    Simple CM for sqlite3 databases. Commits everything at exit.
    """
    def __init__(self, path):
        self.path = path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()


def initdb(path = db_path):
    feed_Tbl_Create = '''
    CREATE TABLE IF NOT EXISTS Feed (
         feed_id INTEGER NOT NULL,
         title TEXT,
         description TEXT,
         url TEXT,
         date_added  TEXT,
         header_modified TEXT,
         header_etag TEXT,
         PRIMARY KEY (feed_id),
         CONSTRAINT uix_0 UNIQUE (title, url)
    );
    '''

    feedItem_Tbl_Create = '''
    CREATE TABLE IF NOT EXISTS FeedItem (
        feeditem_id INTEGER NOT NULL,
        feed_id INTEGER NOT NULL,
        title TEXT,
        content TEXT,
        summary TEXT,
        url TEXT,
        author TEXT,
        date_published TEXT,
        date_updated TEXT,
        is_read INTEGER DEFAULT(1),
        PRIMARY KEY (feeditem_id),
        CONSTRAINT uix_0 UNIQUE (feed_id, url),
        FOREIGN KEY(feed_id) REFERENCES "Feed" (feed_id),
        CHECK (is_read IN (0, 1))
    );
    '''

    print "Initializing Database..."
    try:
        with session_scope(path) as db:
            db.execute(feedItem_Tbl_Create)
            db.execute(feed_Tbl_Create)
    except:
        print "Error Initializing Database: {}".format(str(sys.exc_info()[1]))