# this set of tests calles a series of endpoints that this API is meant to expose and tests them for content
import requests
import re


ENDPOINTS = [
    {
        'label': 'GNAF landing page',
        'uri': 'http://localhost:5000',
        'headers': None,
        'regex': '<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF landing page slash',
        'uri': 'http://localhost:5000/',
        'headers': None,
        'regex': '<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF as a DCAT Distribution, HTML',
        'uri': 'http://localhost:5000?_view=dcat',
        'headers': None,
        'regex': '<h1>G-NAF - distributed as Linked Data</h1>'
    },
    {
        'label': 'GNAF as a DCAT Distribution, RDF (turtle), QSA',
        'uri': 'http://localhost:5000?_format=text/turtle',
        'headers': None,
        'regex': 'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a DCAT Distribution, RDF (turtle), file ext',
        'uri': 'http://localhost:5000/index.ttl',
        'headers': None,
        'regex': 'dct:title "G-NAF - distributed as Linked Data" ;'
    },
    {
        'label': 'GNAF as a DCAT Distribution, RDF (turtle), Accept',
        'uri': 'http://localhost:5000',
        'headers': {'Accept': 'text/turtle'},
        'regex': 'dct:title "G-NAF - as Linked Data" ;'
    },
    {
        'label': 'GNAF as a VOID Dataset, RDF (turtle)',
        'uri': 'http://localhost:5000?_view=void',
        'headers': None,
        'regex': '<http://linked.data.gov.au/dataset/gnaf> a void:Dataset ;'
    },
    {
        'label': 'GNAF as a REG Register, HTML',
        'uri': 'http://localhost:5000',
        'headers': None,
        'regex': '<h1>G-NAF - as a Register of Registers</h1>'
    },
    {
        'label': 'GNAF as a REG Register, RDF (turtle)',
        'uri': 'http://localhost:5000',
        'headers': None,
        'regex': '<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    },
    # {
    #     'label': '',
    #     'uri': 'http://linked.data.gov.au/dataset/gnaf?_format=text/turtle',
    #     'headers': {},
    #     'regex': 'dct:title \"GNAF Dataset Distribution as Linked Data\"\^\^xsd:string ;'
    # },
    # {
    #     'label': '',
    #     'uri': 'http://gnafld.net/sparql?query=SELECT(COUNT(%3Fs)AS%20%3Fc)%20WHERE%20%7B%20%3Fs%20a%20%3Chttp%3A%2F%2Flinked.data.gov.au%2Fdef%2Fgnaf%23Locality%3E%20.%20%7D',
    #     'headers': {},
    #     'regex': '15926'
    # }
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
        assert valid_endpoint_content(e['uri'], e['headers'], e['regex']), e['label']
