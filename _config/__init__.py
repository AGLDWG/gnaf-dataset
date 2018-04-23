from os.path import dirname, realpath, join, abspath
import psycopg2

APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

PAGE_SIZE = 10000

MB_2011_COUNT = 347627
URI_MB_2011_CLASS = 'http://gnafld.net/def/2011MB'
URI_MB_2011_INSTANCE_BASE = 'http://reference.data.gov.au/asgs/MB2011/'

MB_2016_COUNT = 358122
URI_MB_2016_CLASS = 'http://gnafld.net/def/MB2016MB'
URI_MB_2016_INSTANCE_BASE = 'http://reference.data.gov.au/asgs/MB2016/'

ADDRESS_COUNT = 14500797
URI_ADDRESS_CLASS = 'http://gnafld.net/def/gnaf#Address'
URI_ADDRESS_INSTANCE_BASE = 'http://gnafld.net/address/'

ADDRESS_SITE_COUNT = 14500797
URI_ADDRESS_SITE_CLASS = 'http://gnafld.net/def/gnaf#AddressSite'
URI_ADDRESS_SITE_INSTANCE_BASE = 'http://gnafld.net/addressSite/'

STREET_LOCALITY_COUNT = 707075
URI_STREETLOCALITY_CLASS = 'http://gnafld.net/def/gnaf#StreetLocality'
URI_STREETLOCALITY_INSTANCE_BASE = 'http://gnafld.net/streetLocality/'

LOCALITY_COUNT = 16445
URI_LOCALITY_CLASS = 'http://gnafld.net/def/gnaf#Locality'
URI_LOCALITY_INSTANCE_BASE = 'http://gnafld.net/locality/'

DB_HOST = 'localhost'
DB_DBNAME = 'gnaf'
DB_USR = 'gnafusr'
DB_PWD = 'technicolour'
DB_SCHEMA = 'gnaf'


SPARQL_AUTH_USR = 'admin'
SPARQL_AUTH_PWD = 'dreamcoat'
SPARQL_QUERY_URI = 'http://52.15.86.52/fuseki/gnaf/query'


def get_db_cursor():
    try:
        connect_str = "host='{}' dbname='{}' user='{}' password='{}'" \
            .format(
            DB_HOST,
            DB_DBNAME,
            DB_USR,
            DB_PWD
        )
        return psycopg2.connect(connect_str).cursor()
    except Exception as e:
        print("Can't connect to DB {}".format(DB_DBNAME))
        print(e)


class reg(object):
    def __init__(self, cursor, row):
        for (attr, val) in zip((d[0] for d in cursor.description), row):
            setattr(self, attr, val)


if __name__ == '__main__':
    pass
