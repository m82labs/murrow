#!/usr/bin/env python
import db
import db.murrow_data as md
import os

if __name__ == '__main__':
    db_path = os.path.join(os.path.expanduser('~'), '.murrow', 'test-murrow.db')
    try:
        os.remove(db_path)
    except:
        print 'No file to remove.'

    tables = ('Feed', 'FeedItem')

    with db.session_scope(db_path) as session:
        print session.row_factory
        db.initdb(db_path)

        table_qry = 'DELETE FROM {};'
        for t in tables:
            print ' - Checking if {} exists...'.format(t,)
            session.execute(table_qry.format(t,))

        print 'Inserting 2 feeds...'
        feed_id = md.add_feed(session, 'http://littlekendra.com/feed')
        md.update_feeditems(session,feed_id)
        feed_id2 = md.add_feed(session, 'http://blogs.harvard.edu/cmusings/feed/')
        md.update_feeditems(session, feed_id2)
        assert (len(md.get_feed(session)) == 2)
        for f in md.get_feed(session):
            print f

        for f in md.get_feed(session):
            print f

        print 'Deleting feed...'
        md.delete_feed(session, 1)
        assert (len(md.get_feed(session)) == 1)

        for f in md.get_feed(session):
            print f
            for fi in md.get_items(session, f[0]):
                print fi

        print 'Marking an article as "Read".'
        md.mark_as_read(session,1)
        for f in md.get_feed(session):
            print f
            for fi in md.get_items(session, f[0]):
                print fi

        print 'Updating the feed'
        print md.update_feeditems(session, 2)
        for f in md.get_feed(session):
            print f