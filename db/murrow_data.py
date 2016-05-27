import feedparser
import html2text
import sys
import re
from time import mktime
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, desc
from . import Base


def is_valid_url(url):
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


def add_feed(session, url):
    """
    Adds a new feed, given a feed URL
    :param url: Feed URL
    """
    try:
        for u in url.split(' '):
            if is_valid_url(u):
                new_feed = Feed.fromURL(u)
                session.add(new_feed)
                session.flush()
                new_feed.update_items(session, 14)
                return "Feed '{}' added.".format(u)
    except:
        return "Error adding feed: {}".format(sys.exc_info()[1])


def get_feed(session, id=0):
    """
    Gets one or more feeds
    :param id: If == 0, get all feeds, otherwise, get the specified feed
    :return: Feed[]
    """
    if id == 0:
        filters = (
            Feed.id > id
        )
    else:
        filters = (
            Feed.id == id
        )
    return session.query(Feed).filter(filters)

def mark_as_read(session, feed_id, url):
    """
    Marks a given feeditem as read.
    """
    feeditem = session.query(FeedItem).filter(FeedItem.feed_id == feed_id, FeedItem.url == url).one()
    feeditem.is_read = 1


class Feed(Base):
    """
    Concerns:
    - Providing data on a specific feed
    - Adding new feed items
    - Retrieving feed items
    """
    __tablename__ = 'Feed'

    id = Column(Integer, unique=True, primary_key=True)
    title = Column(String)
    description = Column(String)
    url = Column(String, unique=True)
    date_added = Column(DateTime)
    header_modified = Column(String)
    header_etag = Column(String)

    @classmethod
    def fromURL(self, u):
        """
        Generates an instance of Feed based on a given
        feed url.
        """
        feed = feedparser.parse(u)
        title = feed['channel']['title']
        description = feed['channel']['description']

        return Feed(title=title, description=description, url=u, date_added=datetime.utcnow())

    def update_items(self,session,days=0):
        """
        Adds new feed items to the database for this feed.
        :param session: SQLAlchemy Session
        :param days: Number of days to look back for new feed items.
        If this is set to 0, it will check the feed headers to see
        if the feed has been modified.

        :return: NA
        """
        if days > 0:
            modified = str(datetime.utcnow() - timedelta(days=days))
            etag = ''
        else:
            modified = self.header_modified
            etag = self.header_etag

        feed = feedparser.parse(self.url, modified=modified, etag=etag)

        for item in feed['entries']:
            # Get the content, prefer plan text
            for c in item.content:
                if c.type == 'text/plain':
                    content = c.value
                    break
                elif c.type == 'text/html':
                    content = html2text.html2text(c.value)
                    break
                else:
                    continue

            if 'content' in locals():
                session.merge(FeedItem(feed_id = self.id, title = item['title'],
                                   content = content, url = item['link'], summary = item['summary'],
                                   author = item['author'], date_published = datetime.fromtimestamp(mktime(item['published_parsed'])),
                                   date_updated = datetime.fromtimestamp(mktime(item['updated_parsed'])),
                                   is_read = 0))

        if hasattr(feed, 'etag'):
            self.header_etag = feed.etag
        if hasattr(feed, 'modified'):
            self.header_modified = feed.modified
        session.flush()

    def get_items (self, session):
        """
        Retrieves feed items for a given feed.
        :return: FeedItem[]
        """
        return session.query(FeedItem).order_by(desc(FeedItem.date_published)).filter(FeedItem.feed_id == self.id)


class FeedItem(Base):
    __tablename__ = 'FeedItem'

    feed_id = Column(Integer,ForeignKey("Feed.id"), nullable=False, primary_key = True)
    title = Column(String)
    content = Column(String)
    summary = Column(String)
    url = Column(String, unique=True, primary_key = True)
    author = Column(String)
    date_published = Column(DateTime)
    date_updated = Column(DateTime)
    is_read = Column(Boolean)