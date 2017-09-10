from os.path import dirname, realpath, join, abspath

APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

URI_MB_2011_CLASS = 'http://reference.data.gov.au/def/ont/asgs#MB2011'
URI_MB_2011_INSTANCE_BASE = 'http://reference.data.gov.au/id/asgs/MB2011/'

URI_MB_2016_CLASS = 'http://reference.data.gov.au/def/ont/asgs#MB2016'
URI_MB_2016_INSTANCE_BASE = 'http://reference.data.gov.au/id/asgs/MB2016/'

URI_ADDRESS_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Address'
URI_ADDRESS_INSTANCE_BASE = 'http://transport.data.gov.au/id/address/'

URI_ADDRESS_SITE_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#AddressSite'
URI_ADDRESS_SITE_INSTANCE_BASE = 'http://transport.data.gov.au/id/addressSite/'

URI_ADDRESS_SITE_GEOCODE_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#AddressSiteGeocode'
URI_ADDRESS_SITE_GEOCODE_INSTANCE_BASE = 'http://transport.data.gov.au/id/addressSiteGeocode/'

URI_STREET_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Street'
URI_STREET_INSTANCE_BASE = 'http://transport.data.gov.au/id/street/'

URI_STREET_LOCALITY_ALIAS_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#StreetLocalityAlias'
URI_STREET_LOCALITY_ALIAS_INSTANCE_BASE = 'http://transport.data.gov.au/id/streetLocalityAlias/'

URI_LOCALITY_ALIAS_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#LocalityAlias'
URI_LOCALITY_ALIAS_INSTANCE_BASE = 'http://transport.data.gov.au/id/localityAlias/'

URI_LOCALITY_CLASS = 'http://reference.data.gov.au/def/ont/gnaf#Locality'
URI_LOCALITY_INSTANCE_BASE = 'http://transport.data.gov.au/id/locality/'

DB_HOST = 'localhost'
DB_DBNAME = 'car587'
DB_USR = 'gnaf'
DB_PWD = ''
DB_SCHEMA = 'gnaf'
