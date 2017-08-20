from os.path import dirname, realpath, join
APP_DIR = dirname(dirname(realpath(__file__)))
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

URI_ADDRESS_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Address'
URI_ADDRESS_INSTANCE_BASE = 'http://transport.data.gov.au/id/address/'

DB_HOST = 'localhost'
DB_DBNAME = 'car587'
DB_USR = 'gnaf'
DB_PWD = 'gnaf'
