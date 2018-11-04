# this set of tests calls a series of endpoints that this API is meant to expose and tests them for content
import requests
import re
import pytest

SYSTEM_URI = 'http://gnafld.net'


def valid_endpoint_content(uri, headers, pattern):
    # dereference the URI
    r = requests.get(uri, headers=headers)

    # parse the content looking for the thing specified in REGEX
    if re.search(pattern, r.content.decode('utf-8'), re.MULTILINE):
        return True
    else:
        return False


def test_gnaf_landing_page_html():
    assert valid_endpoint_content(
        SYSTEM_URI,
        None,
        r'<h1>G-NAF - distributed as Linked Data</h1>'
    ), 'GNAF landing page HTML failed'


def test_gnaf_landing_page_slash_html():
    assert valid_endpoint_content(
        f"{SYSTEM_URI}/",
        None,
        r'<h1>G-NAF - distributed as Linked Data</h1>'
    ), 'GNAF landing page with a slash HTML failed'


def test_gnaf_landing_page_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f"{SYSTEM_URI}/index.ttl",
        None,
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF landing page RDF (turtle) file extension failed'


def test_gnaf_landing_page_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f"{SYSTEM_URI}/?_format=text/turtle",
        None,
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF landing page RDF (turtle) QSA failed'


def test_gnaf_landing_page_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}',
        {'Accept': 'text/turtle'},
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF landing page RDF (turtle) Accept header failed'


def test_gnaf_dcat_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_view=dcat',
        None,
        '<h1>G-NAF - distributed as Linked Data</h1>'
    ), 'GNAF as a DCAT Distribution, HTML failed'


def test_gnaf_dcat_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_format=text/turtle',
        None,
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF as a DCAT Distribution, RDF (turtle), QSA failed'


def test_gnaf_dcat_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}',
        {'Accept': 'text/turtle'},
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF as a DCAT Distribution, RDF (turtle), Accept failed'


def test_gnaf_void_view_rdf_turtle():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_view=void',
        None,
        r'<http://linked.data.gov.au/dataset/gnaf> a void:Dataset ;'
    ), 'GNAF as a VOID Dataset, RDF (turtle) failed'


def test_gnaf_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_view=reg',
        None,
        r'<h1>G-NAF - as a Register of Registers</h1>'
    ), 'GNAF as a REG Register, HTML failed'


def test_gnaf_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_view=reg',
        None,
        r'<h1>G-NAF - as a Register of Registers</h1>'
    ), 'GNAF as a REG Register, HTML failed'


def test_gnaf_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_view=reg&_format=text/turtle',
        None,
        r'<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    ), 'GNAF as a REG Register, RDF (turtle) failed'


def test_gnaf_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}?_view=reg',
        {'Accept': 'text/xml, text/turtle, text/html'},
        r'<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    ), 'GNAF as a REG Register, RDF (turtle), Accept with preferences failed'


def test_gnaf_sparql_endpoint_localities_count():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sparql?query=SELECT(COUNT(%3Fs)AS%20%3Fc)%20WHERE%20%7B%20%3Fs%20a%20%3Chttp%3A%2F%2Flinked.data.gov.au%2Fdef%2Fgnaf%23Locality%3E%20.%20%7D',
        None,
        r'15926'
    ), 'SPARQL endpoint localities count == 150 failed'


def test_gnaf_address_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/',
        None,
        r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#Address">http:\/\/linked.data.gov.au\/def\/gnaf#Address<\/a><\/em> class items<\/h2>'
    ), 'Address Register as GNAF HTML failed'


def test_gnaf_address_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    ), 'Address Register as GNAF RDF (turtle) QSA failed'


def test_gnaf_address_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    ), 'Address Register as GNAF RDF (turtle) Accept header failed'


def test_gnaf_address_instance_GAACT714857880_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880',
        None,
        r'<h1>Address GAACT714857880</h1>'
    ), 'Address GAACT714857880 as GNAF HTML failed'


@pytest.mark.skip('Address GAACT714857880 as GNAF RDF (turtle) file extension not yet implemented')
def test_gnaf_address_instance_GAACT714857880_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880.ttl',
        None,
        r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    ), 'Address GAACT714857880 as GNAF RDF (turtle) file extension failed'


def test_gnaf_address_instance_GAACT714857880_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_format=text/turtle',
        None,
        r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    ), 'Address GAACT714857880 as GNAF RDF (turtle) QSA failed'


def test_gnaf_address_instance_GAACT714857880_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_format=text/turtle',
        {'Accept': 'text/xml,text/turtle,text/html'},
        r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    ), 'Address GAACT714857880 as GNAF RDF (turtle) Accept header failed'


def test_gnaf_street_locality_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/',
        None,
        r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality">http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality<\/a><\/em> class items<\/h2>'
    ), 'Street Locality Register as GNAF HTML failed'


def test_gnaf_street_locality_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/?_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1> a <http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality> ;'
    ), 'Street Locality Register as GNAF RDF (turtle) QSA failed'


def test_gnaf_street_locality_register_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1> a <http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality> ;'
    ), 'Street Locality Register as GNAF RDF (turtle) Accept header failed'


@pytest.mark.skip('Street Locality Register as GNAF RDF (turtle) Accept header not yet implemented')
def test_gnaf_street_locality_register_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/index.ttl',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1> a <http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality> ;'
    ), 'Street Locality Register as GNAF RDF (turtle) file extension failed'


def test_gnaf_street_locality_instance_ACT1046_gnaf_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046',
        None,
        r'<h1>Street Locality ACT1046<\/h1>'
    ), 'Street Locality ACT1046 as GNAF HTML failed'


@pytest.mark.skip('Street Locality ACT1046 as GNAF RDF (turtle) file extension not yet implemented')
def test_gnaf_street_locality_instance_ACT1046_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046.ttl',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1046> a gnaf:StreetLocality ;'
    ), 'Street Locality ACT1046 as GNAF RDF (turtle) file extension failed'


def test_gnaf_street_locality_instance_ACT1046_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1046> a gnaf:StreetLocality ;'
    ), 'Street Locality ACT1046 as GNAF RDF (turtle) QSA failed'


def test_gnaf_street_locality_ACT1046_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1046> a gnaf:StreetLocality ;'
    ), 'Street Locality ACT1046 as GNAF RDF (turtle) Accept header failed'


def test_gnaf_locality_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/',
        None,
        r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#Locality">http:\/\/linked.data.gov.au\/def\/gnaf#Locality<\/a><\/em> class items<\/h2>'
    ), 'Locality Register as GNAF HTML failed'


@pytest.mark.skip('Locality Register as GNAF RDF (turtle) file extension not yet implemented')
def test_gnaf_locality_register_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/index.ttl',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    ), 'Locality Register as GNAF RDF (turtle) file extension failed'


def test_gnaf_locality_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    ), 'Locality Register as GNAF RDF (turtle) QSA failed'


def test_gnaf_locality_register_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    ), 'Locality Register as GNAF RDF (turtle) Accept header failed'


if __name__ == '__main__':
    pass

