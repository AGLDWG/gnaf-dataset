# this set of tests calles a series of endpoints that this API is meant to expose and tests them for content
import requests
import re
import subprocess

SYSTEM_URI = 'http://gnafld.net'
ENDPOINTS = [
    {
        'label': 'GNAF landing page',
        'uri': '{}'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF landing page slash',
        'uri': '{}/'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF landing page RDF (turtle) file extension',
        'uri': '{}/index.ttl'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF landing page RDF (turtle) QSA',
        'uri': f'{SYSTEM_URI}/?_format=text/turtle',
        'headers': None,
        'regex': r'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF landing page RDF (turtle) Accept header',
        'uri': f'{SYSTEM_URI}/',
        'headers': {'Accept': 'text/turtle'},
        'regex': r'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a DCAT Distribution, HTML',
        'uri': '{}?_view=dcat'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF as a DCAT Distribution, RDF (turtle), QSA',
        'uri': '{}?_format=text/turtle'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a DCAT Distribution, RDF (turtle), Accept',
        'uri': '{}'.format(SYSTEM_URI),
        'headers': {'Accept': 'text/turtle'},
        'regex': r'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a VOID Dataset, RDF (turtle)',
        'uri': '{}?_view=void'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'<http://linked.data.gov.au/dataset/gnaf> a void:Dataset ;'
    },
    {
        'label': 'GNAF as a REG Register, HTML',
        'uri': '{}?_view=reg'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'<h1>G-NAF - as a Register of Registers</h1>'
    },
    {
        'label': 'GNAF as a REG Register, RDF (turtle)',
        'uri': '{}?_view=reg&_format=text/turtle'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    },
    {
        'label': 'GNAF as a REG Register, RDF (turtle), Accept with preferences',
        'uri': '{}?_view=reg'.format(SYSTEM_URI),
        'headers': {'Accept': 'text/xml,text/turtle,text/html'},
        'regex': r'<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    },
    {
        'label': 'SPARQL endpoint localities count == 150',
        'uri': '{}/sparql?query=SELECT(COUNT(%3Fs)AS%20%3Fc)%20WHERE%20%7B%20%3Fs%20a%20%3Chttp%3A%2F%2Flinked.data.gov.au%2Fdef%2Fgnaf%23Locality%3E%20.%20%7D'.format(SYSTEM_URI),
        'headers': {},
        'regex': r'15926'
    },
    {
        'label': 'Address Register as GNAF HTML',
        'uri': f'{SYSTEM_URI}/address/',
        'headers': None,
        'regex': r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#Address">http:\/\/linked.data.gov.au\/def\/gnaf#Address<\/a><\/em> class items<\/h2>'
    },
    {
        'label': 'Address Register as GNAF RDF (turtle) QSA',
        'uri': f'{SYSTEM_URI}/address/?_format=text/turtle',
        'headers': None,
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    },
    {
        'label': 'Address Register as GNAF RDF (turtle) Accept header',
        'uri': f'{SYSTEM_URI}/address/',
        'headers': {'Accept': 'text/turtle'},
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    },
    {
        'label': 'Address GAACT714857880 as GNAF HTML',
        'uri': '{}/address/GAACT714857880'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'<h1>Address GAACT714857880</h1>'
    },
    # { #TODO
    #     'label': 'Address GAACT714857880 as GNAF RDF (turtle) file extension',
    #     'uri': f'{SYSTEM_URI}/address/GAACT714857880.ttl',
    #     'headers': None,
    #     'regex': r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    # },
    {
        'label': 'Address GAACT714857880 as GNAF RDF (turtle) QSA',
        'uri': '{}/address/GAACT714857880?_format=text/turtle'.format(SYSTEM_URI),
        'headers': None,
        'regex': r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    },
    {
        'label': 'Address GAACT714857880 as GNAF RDF (turtle) Accept header',
        'uri': '{}/address/GAACT714857880?_format=text/turtle'.format(SYSTEM_URI),
        'headers': {'Accept': 'text/xml,text/turtle,text/html'},
        'regex': r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    },
    {
        'label': 'Street Locality Register as GNAF HTML',
        'uri': f'{SYSTEM_URI}/streetLocality/',
        'headers': None,
        'regex': r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality">http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality<\/a><\/em> class items<\/h2>'
    },
    {
        'label': 'Street Locality Register as GNAF RDF (turtle) QSA',
        'uri': f'{SYSTEM_URI}/streetLocality/?_format=text/turtle',
        'headers': None,
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1> a <http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality> ;'
    },
    {
        'label': 'Street Locality Register as GNAF RDF (turtle) Accept header',
        'uri': f'{SYSTEM_URI}/streetLocality/',
        'headers': {'Accept': 'text/turtle'},
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1> a <http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality> ;'
    },
    {
        'label': 'Street Locality ACT1046 as GNAF HTML',
        'uri': f'{SYSTEM_URI}/streetLocality/ACT1046',
        'headers': None,
        'regex': r'<h1>Street Locality ACT1046<\/h1>'
    },
    # { #TODO
    #     'label': 'Street Locality ACT1046 as GNAF RDF (turtle) file extension',
    #     'uri': f'{SYSTEM_URI}/streetLocality/ACT1046.ttl',
    #     'headers': None,
    #     'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1046> a gnaf:StreetLocality ;'
    # },
    {
        'label': 'Street Locality ACT1046 as GNAF RDF (turtle) QSA',
        'uri': f'{SYSTEM_URI}/streetLocality/ACT1046?_format=text/turtle',
        'headers': None,
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1046> a gnaf:StreetLocality ;'
    },
    {
        'label': 'Street Locality ACT1046 as GNAF RDF (turtle) Accept header',
        'uri': f'{SYSTEM_URI}/streetLocality/ACT1046',
        'headers': {'Accept': 'text/turtle'},
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1046> a gnaf:StreetLocality ;'
    },
    {
        'label': 'Locality Register as GNAF HTML',
        'uri': f'{SYSTEM_URI}/locality/',
        'headers': None,
        'regex': r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#Locality">http:\/\/linked.data.gov.au\/def\/gnaf#Locality<\/a><\/em> class items<\/h2>'
    },
    # { #TODO
    #     'label': 'Locality Register as GNAF RDF (turtle) file extension',
    #     'uri': f'{SYSTEM_URI}/locality/index.ttl',
    #     'headers': None,
    #     'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    # },
    {
        'label': 'Locality Register as GNAF RDF (turtle) QSA',
        'uri': f'{SYSTEM_URI}/locality/?_format=text/turtle',
        'headers': None,
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    },
    {
        'label': 'Locality Register as GNAF RDF (turtle) Accept header',
        'uri': f'{SYSTEM_URI}/locality/',
        'headers': {'Accept': 'text/turtle'},
        'regex': r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    }
]


def valid_endpoint_content(uri, headers, pattern):
    # dereference the URI
    r = requests.get(uri, headers=headers)

    # parse the content looking for the thing specified in REGEX
    if re.search(pattern, r.content.decode('utf-8'), re.MULTILINE):
        return True
    else:
        return False


def test_valid_endpoint_content():
    for e in ENDPOINTS:
        assert valid_endpoint_content(e['uri'], e['headers'], e['regex']), f"{e['label']} failed."


if __name__ == '__main__':
    result = subprocess.run('pytest test_ld_endpoints.py')

