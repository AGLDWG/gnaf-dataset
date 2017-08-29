from os.path import dirname, realpath, join
APP_DIR = dirname(dirname(realpath(__file__)))
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

URI_ADDRESS_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Address'
URI_ADDRESS_INSTANCE_BASE = 'http://transport.data.gov.au/id/address/'

URI_ADDRESS_SITE_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#AddressSite'
URI_ADDRESS_SITE_INSTANCE_BASE = 'http://transport.data.gov.au/id/addressSite/'

URI_STREET_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Street'
URI_STREET_INSTANCE_BASE = 'http://transport.data.gov.au/id/street/'

URI_LOCALITY_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Locality'
URI_LOCALITY_INSTANCE_BASE = 'http://transport.data.gov.au/id/locality/'

DB_HOST = 'localhost'
DB_DBNAME = 'linearint'
DB_USR = 'josephabhayaratna'
DB_PWD = ''
DB_SCHEMA = 'gnaf'