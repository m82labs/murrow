import os, sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager

Base = declarative_base()
db_path = 'sqlite:///' + os.path.join(os.path.expanduser('~'), '.murrow', 'murrow.db')
sql = create_engine(db_path)
Session = sessionmaker(bind=sql, expire_on_commit=False)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def initdb():
    print "Initializing Database..."
    try:
        Base.metadata.create_all(sql)
    except:
        print "Error Initializing Database: {}".format(str(sys.exc_info()[2]))