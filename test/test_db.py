#!/usr/bin/env python
import db
import db.murrow_data as md
import os

if __name__ == '__main__':
    db_path = os.path.join(os.path.expanduser('~'), '.murrow', 'test-murrow.db')
    tables = ('Feed', 'FeedItem')

    with db.session_scope(db_path) as session:
        table_qry = 'DELETE FROM {};'
        for t in tables:
            print ' - Checking if {} exists...'.format(t,)
            session.execute(table_qry.format(t,))
        print 'Tables created.'

    with db.session_scope(db_path) as session:
        print 'Inserting 2 feeds...'
        print md.add_feed(session, 'http://littlekendra.com/feed')
        print md.add_feed(session, 'http://krebsonsecurity.com/feed/')

    with db.session_scope(db_path) as session:
        print 'Getting feed list...'
        try:
            assert( len(md.get_feed(session)) == 2 )
        except AssertionError, e:
            print e

    with db.session_scope(db_path) as session:
        print 'Deleting feed'
