# -*- coding: utf-8 -*-
import feedparser
import html2text
import math
import pytz
import re
from time import mktime,sleep
from datetime import datetime
from db import session_scope


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

    session.execute(feedItem_delete_qry, params)
    session.execute(feed_delete_qry, params)


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
                return session.lastrowid
    except:
        return -1


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


def update_feeditems(session, id):
    """
    Adds new feed items to the database for this feed and update the FTS index
    :param session: SQLite Session
    :return: NA
    """
    header_get_params = (id,)
    fts_update_params = (id,)

    feed_get_headers_qry = 'SELECT header_modified, header_etag, url FROM Feed WHERE feed_id = ?;'
    feeditem_upsert_qry = '''
    INSERT INTO FeedItem (
        feed_id,
        title,
        content,
        url,
        summary,
        author,
        date_published,
        date_updated
    )
    SELECT ?, ?, ?, ?, ?, ?, ?, ?
    WHERE NOT EXISTS (
        SELECT  1
        FROM    FeedItem
        WHERE   feed_id = ?
                AND url = ?
    );
    '''
    fts_update_qry = '''
    INSERT INTO FTS_FeedItem ( feeditem_id, content )
    SELECT  feeditem_id,
            content
    FROM    FeedItem
    WHERE   feed_id = ?
            AND NOT EXISTS (
                SELECT  1
                FROM    FTS_FeedItem
                WHERE   feeditem_id = FeedItem.Feeditem_id
            );
    '''
    feed_header_upsert_qry = '''
    UPDATE Feed
    SET header_etag = ?,
    header_modified = ?
    WHERE feed_id = ?;'''

    session.execute(feed_get_headers_qry, header_get_params)
    headers = session.fetchone()

    modified = headers[0]
    etag = headers[1]

    feed = feedparser.parse(headers[2], etag = etag, modified = modified)
    if feed.status == 301 or feed.status == 200:
        for item in feed['entries']:
            # Get the content, prefer plan text
            if hasattr(item, "content"):
                for c in item.content:
                    if c.type == 'text/html':
                        h = html2text.HTML2Text()
                        h.inline_links = False
                        h.wrap_links = False
                        content = h.handle(c.value)
                        break
                    elif c.type == 'text/plain':
                        content = c.value
                        break
                    else:
                        continue
            else:
                content = ""

            published = None
            updated = None

            if 'published_parsed' in item:
                published = datetime.fromtimestamp(mktime(item['published_parsed']))
            elif 'updated_parsed' in item:
                published = datetime.fromtimestamp(mktime(item['updated_parsed']))
                updated = datetime.fromtimestamp(mktime(item['updated_parsed']))

            if 'content' in locals():
                upsert_params = (id, item['title'], content, item['link'],
                                 item['summary'], item['author'],
                                 published, updated, id, item['link'])
                session.execute(feeditem_upsert_qry, upsert_params)

        if hasattr(feed, 'etag'):
            new_etag = feed.etag
        else:
            new_etag = None

        new_modified = datetime.now(tz = pytz.timezone('GMT')).strftime('%a, %d %b %Y %H:%M:%S %Z')
        header_upsert_params = (new_etag, new_modified, id)
        session.execute(feed_header_upsert_qry, header_upsert_params)
        session.execute(fts_update_qry, fts_update_params)
        return len(feed['entries'])
    else:
        return 0


def update_all_feeds(session):
    """
    Loops through and updates ALL feeds.
    returns: Number of feed items updated.
    """
    updates = 0
    for f in get_feed(session):
        updates += update_feeditems(session, f['feed_id'])
    return updates


def update_read_speed(session):
    """
    Updates the reading speed for time estimates.
    The initial implementation uses a global vaiable.
    In the future, this number is calculated on a per feed basis.
    """
    get_read_data_qry = 'SELECT (time_to_read_sec/word_count) AS sec_word FROM ReadAnalytics;'
    data = [i['sec_word'] for i in session.execute(get_read_data_qry)]
    trimmed_data = sorted(data)[int(math.ceil((len(data) - 1) * .1)):int(math.floor((len(data) - 1) * .9))]
    if len(trimmed_data) == 0:
        return 0
    else:
        return sum(trimmed_data) / len(trimmed_data)


def background_updater(minutes):
    """
    Runs background update tasks, currently only feed updates
    """
    while True:
        with session_scope() as session:
            updates = update_all_feeds(session)
        sleep(minutes*60)


def get_items(session, id):
    """
    Retrieves feed items for a given feed.
    """
    params = (id,)

    feeditem_get_list_qry = '''
    SELECT  feeditem_id,
            title,
            content,
            author,
            url,
            date_published,
            IFNULL(date_updated,date_published) AS date_updated,
            is_read
    FROM    FeedItem
    WHERE   feed_id = ?
    ORDER BY date_updated DESC;'''

    session.execute(feeditem_get_list_qry, params)
    return session.fetchall()


def search_items(session, search_qry):
    """
    Does a full text search based on the users query.
    @search_qry: comma separated list of search terms
    """
    fts_query = '''
    SELECT  feeditem_id,
            title,
            content,
            author,
            url,
            date_published,
            IFNULL(date_updated,date_published) AS date_updated,
            is_read
    FROM    FeedItem
    WHERE   feeditem_id IN (
            SELECT  feeditem_id
            FROM    FTS_FeedItem
            WHERE   content MATCH ?
    )
    ORDER BY date_updated DESC;'''
    search_str = '('
    last_op = None
    closing_paren = ')'
    for term in (reversed(sorted(search_qry.split(',')))):
        operator = 'OR'
        if search_str == '(':
            search_str += ' "' + term + '" '
        else:
            if '+' in term:
                term = term.replace('+', '')
                operator = 'AND'
                closing_paren = ''
                if last_op != operator:
                    search_str += ") "

            search_str += operator + ' "' + term + '" '
        last_op = operator

    search_str += closing_paren

    session.execute(fts_query, (search_str,))
    return session.fetchall()


def mark_as_read(session, id, word_count, time_to_read):
    """
    Marks a given feeditem as read.
    """
    fi_params = (id,)
    ra_params = (id, word_count, time_to_read, datetime.utcnow())
    feeditem_update_qry = 'UPDATE FeedItem SET is_read = 1 WHERE feeditem_id = ?;'
    readanalytics_insert_qry = 'INSERT INTO ReadAnalytics ( feeditem_id, word_count, time_to_read_sec, date_read ) VALUES ( ?, ?, ?, ?);'
    session.execute(feeditem_update_qry, fi_params)
    session.execute(readanalytics_insert_qry, ra_params)
