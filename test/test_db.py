#!/usr/bin/env python
import db
import db.murrow_data as md
import os

if __name__ == '__main__':
    db_path = os.path.join(os.path.expanduser('~'), '.murrow', 'test-murrow.db')
    tables = ('Feed', 'FeedItem')

    with db.session_scope(db_path) as session:
        db.initdb(db_path)

        table_qry = 'DELETE FROM {};'
        for t in tables:
            print ' - Checking if {} exists...'.format(t,)
            session.execute(table_qry.format(t,))
        print 'Tables created.'

        print 'Inserting 2 feeds...'
        print md.add_feed(session, 'http://littlekendra.com/feed')
        print md.add_feed(session, 'http://krebsonsecurity.com/feed/')
        assert (len(md.get_feed(session)) == 2)

        print 'Deleting feed...'
        md.delete_feed(session,1)
        assert (len(md.get_feed(session)) == 1)

        print 'Updating feed...'
        md.update_feeditems(session, 2)
