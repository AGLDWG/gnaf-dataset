from collections import defaultdict
from psycopg2 import pool
from contextlib import contextmanager

from _config import DB_HOST, DB_PORT, DB_DBNAME, DB_USR, DB_PWD


connect_str = "host='{}' port='{}' dbname='{}' user='{}' password='{}'" \
    .format(DB_HOST, DB_PORT, DB_DBNAME, DB_USR, DB_PWD)
try:
    tcp = pool.ThreadedConnectionPool(minconn=8, maxconn=24, dsn=connect_str)
except Exception as e:
    print("Can't connect to DB {}".format(DB_DBNAME))
    print(e)


@contextmanager
def get_db_connection():
    con = None
    try:
        try:
            con = tcp.getconn()
        except Exception as e:
            print("Can't connect a db connection from the connection pool.".format(DB_DBNAME))
            raise e
        yield con
    finally:
        if con is not None:
            tcp.putconn(con)

cursor_pools = defaultdict(list)

@contextmanager
def get_db_cursor(con=None):
    put_con = False
    if con is None:
        try:
            con = tcp.getconn()
            put_con = True
        except Exception as e:
            print("Can't connect a db connection from the connection pool.")
            raise e

    con_id = id(con)
    cursor_pool = cursor_pools[con_id]
    cur = None
    try:
        try:
            cur = cursor_pool.pop(0)
        except IndexError:
            try:
                cur = con.cursor()
            except Exception as e:
                print("Can't get a cursor from the connection.")
                print(e)
        yield cur
    finally:
        if cur is not None:
            cursor_pool.append(cur)
        if put_con:
            tcp.putconn(con)


class reg(object):
    def __init__(self, cursor, row):
        for (attr, val) in zip((d[0] for d in cursor.description), row):
            setattr(self, attr, val)
