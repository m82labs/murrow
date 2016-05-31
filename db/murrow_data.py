import feedparser
import html2text
import sys
import re
from time import mktime
from dateutil import parser
from datetime import datetime, timedelta


def is_valid_url(url):
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


def delete_feed(session, id):
    """
    Deletes a selected feed.
    :param id: id of feed to delete
    :return: NA
    """
    feedItem_delete_qry = 'DELETE FROM FeedItem WHERE feed_id = ?;'
    feed_delete_qry = 'DELETE FROM Feed WHERE feed_id = ?;'

    params = (id,)

    session.execute(feedItem_delete_qry,params)
    session.execute(feed_delete_qry,params)


def add_feed(session, url):
    """
    Adds a new feed, given a feed URL
    :param url: Feed URL
    """

    feed_add_qry = '''
    INSERT INTO Feed ( title, description, url, date_added )
    VALUES ( ?, ?, ?, ? );'''

    try:
        for u in url.split(' '):
            if is_valid_url(u):
                feed = feedparser.parse(u)
                title = feed['channel']['title']
                description = feed['channel']['description']

                params = (title, description, u, datetime.utcnow())
                session.execute(feed_add_qry, params)
                return "Feed '{}' added.".format(u)
    except:
        return "Error adding feed: {}".format(sys.exc_info()[1])


def get_feed(session, id=0):
    """
    Gets one or more feeds
    :param id: If == 0, get all feeds, otherwise, get the specified feed
    :return: Feed[]
    """
    params = (id,)

    feed_get_qry = '''
    SELECT  feed_id,
            title,
            description,
            url,
            date_added,
            header_modified,
            header_etag,
            ( SELECT COUNT(1) FROM FeedItem WHERE is_read = 0 AND feed_id = Feed.feed_id ) AS unread_count
    FROM    Feed'''

    feed_get_all_qry = '''
    WHERE   0 = ?;
    '''

    feed_get_single_qry = '''
    WHERE   feed_id = ?;
    '''

    if id == 0:
        final_qry = feed_get_qry + feed_get_all_qry
    else:
        final_qry = feed_get_qry + feed_get_single_qry

    session.execute(final_qry, params)
    return session.fetchall()


def mark_as_read(session, id):
    """
    Marks a given feeditem as read.
    """
    params = (id,)
    feeditem_update_qry = 'UPDATE FeedItem SET is_read = 1 WHERE feeditem_id = ?;'
    session.execute(feeditem_update_qry, params)


def update_feeditems(session, id):
    """
    Adds new feed items to the database for this feed.
    :param session: SQLAlchemy Session
    :return: NA
    """
    params = (id,)

    feed_get_headers_qry = 'SELECT header_modified, header_etag, url FROM Feed WHERE feed_id = ?;'
    feeditem_upsert_qry = '''
    INSERT OR REPLACE INTO FeedItem ( feed_id, title, content, url, summary, author, date_published, date_updated )
    ( ?, ?, ?, ?, ?, ?, ?, ?);
    '''

    session.execute(feed_get_headers_qry, params)
    headers = session.fetchone()

    modified = unicode(headers[0])
    etag = unicode(headers[1])

    feed = feedparser.parse(headers[2], etag = etag, modified = modified)

    if feed.status == 200:
        for item in feed['entries']:
            # Get the content, prefer plan text
            if hasattr(item,"content"):
                for c in item.content:
                    if c.type == 'text/plain':
                        content = c.value
                        break
                    elif c.type == 'text/html':
                        content = html2text.html2text(c.value)
                        break
                    else:
                        continue
            else:
                content = ""

            if 'content' in locals():
                session.merge(FeedItem(feed_id = self.id, title = item['title'],
                                   content = content, url = item['link'], summary = item['summary'],
                                   author = item['author'], date_published = datetime.fromtimestamp(mktime(item['published_parsed'])),
                                   date_updated = datetime.fromtimestamp(mktime(item['updated_parsed']))
                                      )
                              )

        if hasattr(feed, 'etag'):
            self.header_etag = feed.etag
        self.header_modified = feed.modified
        session.flush()
        return len(feed['entries'])
    else:
        return 0

def get_item_list(session, id):
    """
    Retrieves feed items for a given feed.
    """
    params = (id,)

    feeditem_get_list_qry = '''
    SELECT  feeditem_id,
            date_updated,
            is_read,
            title
    FROM    FeedItem
    WHERE   feed_id = ?;'''

    session.execute(feeditem_get_list_qry, params)
    return session.fetchall()
