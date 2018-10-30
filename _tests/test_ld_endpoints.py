# this set of tests calles a series of endpoints that this API is meant to expose and tests them for content
import requests
import re

SYSTEM_URI = 'http://gnafld.net'
ENDPOINTS = [
    {
        'label': 'GNAF landing page',
        'uri': '{}'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF landing page slash',
        'uri': '{}/'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF/index.ttl',
        'uri': '{}/index.ttl'.format(SYSTEM_URI),
        'headers': None,
        'regex': 'dct:title "G-NAF - distributed as Linked Data" ;'
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
        'regex': 'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a DCAT Distribution, RDF (turtle), Accept',
        'uri': '{}'.format(SYSTEM_URI),
        'headers': {'Accept': 'text/turtle'},
        'regex': 'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a VOID Dataset, RDF (turtle)',
        'uri': '{}?_view=void'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<http://linked.data.gov.au/dataset/gnaf> a void:Dataset ;'
    },
    {
        'label': 'GNAF as a REG Register, HTML',
        'uri': '{}?_view=reg'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<h1>G-NAF - as a Register of Registers</h1>'
    },
    {
        'label': 'GNAF as a REG Register, RDF (turtle)',
        'uri': '{}?_view=reg&_format=text/turtle'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    },
    {
        'label': 'GNAF as a REG Register, RDF (turtle), Accept with preferences',
        'uri': '{}?_view=reg'.format(SYSTEM_URI),
        'headers': {'Accept': 'text/xml,text/turtle,text/html'},
        'regex': '<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    },
    {
        'label': 'SPARQL endpoint localities count == 150',
        'uri': '{}/sparql?query=SELECT(COUNT(%3Fs)AS%20%3Fc)%20WHERE%20%7B%20%3Fs%20a%20%3Chttp%3A%2F%2Flinked.data.gov.au%2Fdef%2Fgnaf%23Locality%3E%20.%20%7D'.format(SYSTEM_URI),
        'headers': {},
        'regex': '15926'
    },
    {
        'label': 'Address GAACT714857880 as GNAF HTML',
        'uri': '{}/address/GAACT714857880'.format(SYSTEM_URI),
        'headers': None,
        'regex': '<h1>Address GAACT714857880</h1>'
    },
    {
        'label': 'Address GAACT714857880 as GNAF RDF (turtle) QSA',
        'uri': '{}/address/GAACT714857880?_format=text/turtle'.format(SYSTEM_URI),
        'headers': None,
        'regex': 'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    },
    {
        'label': 'Address GAACT714857880 as GNAF RDF (turtle) Accept',
        'uri': '{}/address/GAACT714857880?_format=text/turtle'.format(SYSTEM_URI),
        'headers': {'Accept': 'text/xml,text/turtle,text/html'},
        'regex': 'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    },
]


def valid_endpoint_content(uri, headers, pattern):
    # dereference the URI
    r = requests.get(uri, headers=headers)

    # parse the content looking for the thing specified in REGEX
    if re.search(pattern, r.content.decode('utf-8'), re.MULTILINE):
        return True
    else:
        return False


if __name__ == '__main__':
    for e in ENDPOINTS:
        if not valid_endpoint_content(e['uri'], e['headers'], e['regex']):
            print(e['label'] + ' failed')
            break
