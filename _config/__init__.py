from os.path import dirname, realpath, join, abspath
import psycopg2

APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

PAGE_SIZE = 10000

URI_MB_2011_CLASS = 'http://gnafld.net/def/2011MB'
URI_MB_2011_INSTANCE_BASE = 'http://reference.data.gov.au/asgs/MB2011/'

URI_MB_2016_CLASS = 'http://gnafld.net/def/MB2016MB'
URI_MB_2016_INSTANCE_BASE = 'http://reference.data.gov.au/asgs/MB2016/'

URI_ADDRESS_CLASS = 'http://gnafld.net/def/gnaf#Address'
URI_ADDRESS_INSTANCE_BASE = 'http://gnafld.net/address/'

URI_ADDRESS_SITE_CLASS = 'http://gnafld.net/def/gnaf#AddressSite'
URI_ADDRESS_SITE_INSTANCE_BASE = 'http://gnafld.net/addressSite/'

URI_STREET_CLASS = 'http://gnafld.net/def/gnaf#StreetLocality'
URI_STREET_INSTANCE_BASE = 'http://gnafld.net/streetLocality/'

URI_LOCALITY_CLASS = 'http://gnafld.net/def/gnaf#Locality'
URI_LOCALITY_INSTANCE_BASE = 'http://gnafld.net/locality/'

DB_HOST = 'localhost'
DB_DBNAME = 'gnaf'
DB_USR = 'gnafusr'
DB_PWD = 'joschmo'
DB_SCHEMA = 'gnaf'


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


def get_vocab_term(vocab_ttl_file, alt_label):
    import rdflib

    g = rdflib.Graph()
    g.load('C:/Users/car587/work/gnaf-ont/codes/' + vocab_ttl_file + '.ttl', format='turtle')
    q = '''
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?uri ?prefLabel
        WHERE {{
            ?uri    skos:prefLabel  ?prefLabel ;
                    skos:altLabel   ?altLabel . 
            FILTER(?altLabel = "{}")
        }}
    '''.format(alt_label)
    for r in g.query(q):
        return r['uri'], r['prefLabel']


if __name__ == '__main__':
    print(get_vocab_term('AliasSubclasses', 'RA'))
