# this set of tests calls a series of endpoints that this API is meant to expose and tests them for content
import requests
import re
import pytest

SYSTEM_URI = 'http://gnafld.net'
#SYSTEM_URI = 'http://localhost:5000'

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
        f'{SYSTEM_URI}/',
        {'Accept': 'text/turtle'},
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF landing page RDF (turtle) Accept header failed'


def test_gnaf_dcat_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=dcat',
        None,
        '<h1>G-NAF - distributed as Linked Data</h1>'
    ), 'GNAF as a DCAT Distribution, HTML failed'


def test_gnaf_dcat_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=dcat&_format=text/turtle',
        None,
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF as a DCAT Distribution, RDF (turtle), QSA failed'


def test_gnaf_dcat_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/',
        {'Accept': 'text/turtle'},
        r'dct:title "G-NAF - distributed as Linked Data" ;'
    ), 'GNAF as a DCAT Distribution, RDF (turtle), Accept failed'


def test_gnaf_void_view_rdf_turtle():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=void',
        None,
        r'<http://linked.data.gov.au/dataset/gnaf> a void:Dataset ;'
    ), 'GNAF as a VOID Dataset, RDF (turtle) failed'


def test_gnaf_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=reg',
        None,
        r'<h1>G-NAF - as a Register of Registers</h1>'
    ), 'GNAF as a REG Register, HTML failed'


def test_gnaf_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=reg',
        None,
        r'<h1>G-NAF - as a Register of Registers</h1>'
    ), 'GNAF as a REG Register, HTML failed'


def test_gnaf_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=reg&_format=text/turtle',
        None,
        r'<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    ), 'GNAF as a REG Register, RDF (turtle) failed'


def test_gnaf_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=reg',
        {'Accept': 'text/xml, text/turtle, text/html'},
        r'<http://linked.data.gov.au/dataset/gnaf> a reg:Register ;'
    ), 'GNAF as a REG Register, RDF (turtle), Accept with preferences failed'


def test_gnaf_sparql_endpoint_localities_count():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/sparql?query=SELECT(COUNT(%3Fs)AS%20%3Fc)%20WHERE%20%7B%20%3Fs%20a%20%3Chttp%3A%2F%2Flinked.data.gov.au%2Fdef%2Fgnaf%23Locality%3E%20.%20%7D',
        None,
        r'15926'
    ), 'SPARQL endpoint localities count == 150 failed'


def test_gnaf_alternates_view_default():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates',
        None,
        rf'<a href="{SYSTEM_URI}/\?_view=reg&_format=text\/html">text\/html<\/a>'
    ), 'GNAF alternates view default failed'


def test_gnaf_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=text/html',
        None,
        rf'<a href="{SYSTEM_URI}/\?_view=reg&_format=text\/html">text\/html<\/a>'
    ), 'GNAF alternates view qsa html failed'


def test_gnaf_alternates_view_json():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=application/json',
        None,
        r'"default_view": "dcat"'
    ), 'GNAF alternates view qsa application/json failed'


@pytest.mark.skip('GNAF alternates view qsa _internal: Internal Server Error')
def test_gnaf_alternates_view_internal():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=_internal',
        None,
        None #TODO
    ), 'GNAF alternates view qsa _internal failed'


def test_gnaf_alternates_view_rdf_turtle():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=text/turtle',
        None,
        r'rdfs:comment "A \'core ontology for registry services\': items are listed in Registers with acceptance statuses"\^\^xsd:string ;'
    ), 'GNAF alternates view qsa text/turtle failed'


def test_gnaf_alternates_view_rdf_xml():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=application/rdf+xml',
        None,
        r'<rdfs:comment rdf:datatype="http:\/\/www\.w3\.org\/2001\/XMLSchema#string">A \'core ontology for registry services\': items are listed in Registers with acceptance statuses<\/rdfs:comment>'
    ), 'GNAF alternates view qsa application/rd+xml failed'


def test_gnaf_alternates_view_rdf_json():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=application/ld+json',
        None,
        r'"@value": "The DCAT view, according to DCATv2 \(2018\)"'
    ), 'GNAF alternates view qsa application/ld+json'


def test_gnaf_alternates_view_rdf_n3():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=text/n3',
        None,
        r'rdfs:comment "VoID is \'an RDF Schema vocabulary for expressing metadata about RDF datasets\'"\^\^xsd:string ;'
    ), 'GNAF alternates view qsa text/n3 failed'


def test_gnaf_alternates_view_n_triples():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/?_view=alternates&_format=application/n-triples',
        None,
        r'<http:\/\/www\.w3\.org\/1999\/02\/22-rdf-syntax-ns#type> <http:\/\/promsns\.org\/def\/alt#View> \.'
    ), 'GNAF alternates view qsa n-triples failed'


def test_gnaf_address_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/',
        None,
        r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#Address">http:\/\/linked.data.gov.au\/def\/gnaf#Address<\/a><\/em> class items<\/h2>'
    ), 'Address Register as GNAF HTML failed'


@pytest.mark.skip('Address Register as GNAF RDF (turtle) file extension not yet implemented')
def test_gnaf_address_register_rdf_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/index.ttl',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    ), 'Address Register as GNAF RDF (turtle) file extension failed'


def test_gnaf_address_register_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    ), 'Address Register as GNAF RDF (turtle) QSA failed'


def test_gnaf_address_register_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933> a <http:\/\/linked.data.gov.au\/def\/gnaf#Address> ;'
    ), 'Address Register as GNAF RDF (turtle) Accept header failed'


def test_gnaf_address_register_alternates_view_default():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=alternates',
        None,
        r'<h2>Alternates view of a <a href="http://purl.org/linked-data/registry#Register">http://purl.org/linked-data/registry#Register</a></h2>'
    ), 'GNAF Address Register alternates view default'


def test_gnaf_address_register_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=alternates&_format=html',
        None,
        r'<h2>Alternates view of a <a href="http://purl.org/linked-data/registry#Register">http://purl.org/linked-data/registry#Register</a></h2>'
    ), 'GNAF Address Register alternates view as html'


def test_gnaf_address_register_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=alternates&_format=text/turtle',
        None,
        r'<http:\/\/linked\.data\.gov\.au\/dataset\/gnaf\/address\/> alt:hasDefaultView'
    ), 'GNAF Address Register alternates view as rdf turtle qsa failed'


def test_gnaf_address_register_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=alternates',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked\.data\.gov\.au\/dataset\/gnaf\/address\/> alt:hasDefaultView'
    ), 'GNAF Address Register alternates view as rdf turtle accept header failed'


def test_gnaf_address_register_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=reg&_format=text/html',
        None,
        r'<a href="http:\/\/linked.data.gov.au\/def\/gnaf#Address">'
    ), 'GNAF Address Register reg view html failed'


def test_gnaf_address_register_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=reg&_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933>'
    ), 'GNAF Address Register reg view rdf turtle qsa failed'


def test_gnaf_address_register_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/?_view=reg',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/address\/GAACT714845933>'
    ), 'GNAF Address Register reg view rdf turtle accept header failed'


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
        f'{SYSTEM_URI}/address/GAACT714857880',
        {'Accept': 'text/xml,text/turtle,text/html'},
        r'rdfs:label "Address GAACT714857880 of Unknown type"\^\^xsd:string ;'
    ), 'Address GAACT714857880 as GNAF RDF (turtle) Accept header failed'


def test_gnaf_address_instance_GAACT714857880_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=alternates&_format=text/html',
        None,
        r'<h3>Instance <a href="http:\/\/linked\.data\.gov\.au\/dataset\/gnaf\/address\/GAACT714857880">http:\/\/linked\.data\.gov\.au\/dataset\/gnaf\/address\/GAACT714857880<\/a><\/h3>'
    ), 'Address GAACT714857880 alternates view html failed'


def test_gnaf_address_instance_GAACT714857880_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=alternates&_format=text/turtle',
        None,
        r'dct:conformsTo <http:\/\/reference\.data\.gov\.au\/def\/ont\/iso19160-1-address> ;'
    ), 'Address GAACT714857880 alternates view rdf turtle qsa failed'


def test_gnaf_address_instance_GAACT714857880_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=alternates',
        {'Accept': 'text/turtle'},
        r'dct:conformsTo <http:\/\/reference\.data\.gov\.au\/def\/ont\/iso19160-1-address> ;'
    ), 'Address GAACT714857880 alternates view rdf turtle accept header failed'


def test_gnaf_address_instance_GAACT714857880_gnaf_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=gnaf&_format=text/html',
        None,
        r'<a href="http:\/\/linked\.data\.gov\.au\/def\/gnaf\/code\/">GNAF codes<\/a>'
    ), 'Address GAACT714857880 gnaf view html failed'


def test_gnaf_address_instance_GAACT714857880_gnaf_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=gnaf&_format=text/turtle',
        None,
        r'<http:\/\/linked\.data\.gov\.au\/dataset\/gnaf\/address\/GAACT714857880> a gnaf:Address ;'
    ), 'Address GAACT714857880 gnaf view rdf turtle qsa failed'


def test_gnaf_address_instance_GAACT714857880_gnaf_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=gnaf',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked\.data\.gov\.au\/dataset\/gnaf\/address\/GAACT714857880> a gnaf:Address ;'
    ), 'Address GAACT714857880 gnaf view rdf turtle accept header failed'


def test_gnaf_address_instance_GAACT714857880_schemaorg_view_rdf_json_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/address/GAACT714857880?_view=schemaorg&_format=application/ld+json',
        None,
        r'"longitude": 149\.06870674'
    ), 'Address GAACT714857880 schemaorg view rdf application/ld+json qsa failed'


def test_gnaf_street_locality_register_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/',
        None,
        r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality">http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality<\/a><\/em> class items<\/h2>'
    ), 'Street Locality Register as GNAF HTML failed'


@pytest.mark.skip('Street Locality Register as GNAF RDF (turtle) file extension not yet implemented')
def test_gnaf_street_locality_register_rdf_turtle_file_extension():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/index.ttl',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/streetLocality\/ACT1> a <http:\/\/linked.data.gov.au\/def\/gnaf#StreetLocality> ;'
    ), 'Street Locality Register as GNAF RDF (turtle) file extension failed'


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


def test_gnaf_street_locality_instance_ACT1046_html():
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


def test_gnaf_street_locality_ACT1046_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=alternates&_format=text/html',
        None,
        rf'<td><a href="{SYSTEM_URI}\/streetLocality\/ACT1046\?_view=dct">dct<\/a><\/td>'
    ), 'Street Locality ACT1046 alternates view as html failed'


def test_gnaf_street_locality_ACT1046_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=alternates&_format=text/turtle',
        None,
        r'rdfs:comment "Dublin Core Terms from the Dublin Core Metadata Initiative"\^\^xsd:string ;'
    ), 'Street Locality ACT1046 alternates view as rdf turtle qsa failed'


def test_gnaf_street_locality_ACT1046_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=alternates',
        {'Accept': 'text/turtle'},
        r'rdfs:comment "Dublin Core Terms from the Dublin Core Metadata Initiative"\^\^xsd:string ;'
    ), 'Street Locality ACT1046 alternates view as rdf turtle accept header failed'


def test_gnaf_street_locality_ACT1046_gnaf_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=gnaf&_format=text/html',
        None,
        r'<a href="http:\/\/linked\.data\.gov\.au\/def\/gnaf">GNAF ontology<\/a>'
    ), 'Street Locality ACT1046 gnaf view as html failed'


def test_gnaf_street_locality_ACT1046_gnaf_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=gnaf&_format=text/turtle',
        None,
        r'<http://linked.data.gov.au/dataset/gnaf/streetLocality/ACT1046> a gnaf:StreetLocality ;'
    ), 'Street Locality ACT1046 gnaf view as rdf turtle qsa failed'


def test_gnaf_street_locality_ACT1046_gnaf_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=gnaf',
        {'Accept': 'text/turtle'},
        r'<http://linked.data.gov.au/dataset/gnaf/streetLocality/ACT1046> a gnaf:StreetLocality ;'
    ), 'Street Locality ACT1046 gnaf view as rdf turtle accept header failed'


def test_gnaf_street_locality_ACT1046_dct_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=dct&_format=text/html',
        None,
        r'<th>Description:<\/th><td>KAMBAH POOL ROAD None<\/td>'
    ), 'Street Locality ACT1046 dct view as html failed'


@pytest.mark.skip('Street Locality ACT1046 dct view as rdf turtle qsa not yet implemented')
def test_gnaf_street_locality_ACT1046_dct_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/streetLocality/ACT1046?_view=dct&_format=text/turtle',
        None,
        None, #TODO
    ), 'Street Locality ACT1046 dct view as rdf turtle qsa failed'


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


def test_gnaf_locality_register_alternates_view_html():
    assert  valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_view=alternates',
        None,
        rf'<td><a href="{SYSTEM_URI}\/locality\/\?_view=alternates">alternates<\/a><\/td>'
    ), 'GNAF Locality Register alternates view html failed'


def test_gnaf_locality_register_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_view=alternates&_format=text/turtle',
        None,
        r'rdfs:comment "A simple list-of-items view taken from the Registry Ontology"\^\^xsd:string ;'
    ), 'GNAF Locality Register alternates view rdf turtle qsa failed'


def test_gnaf_locality_register_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_view=alternates',
        {'Accept': 'text/turtle'},
        r'rdfs:comment "A simple list-of-items view taken from the Registry Ontology"\^\^xsd:string ;'
    ), 'GNAF Locality Register alternates view rdf turtle accept header failed'


def test_gnaf_locality_register_reg_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_view=reg&_format=text/html',
        None,
        r'<h2>Of <em><a href="http:\/\/linked.data.gov.au\/def\/gnaf#Locality">http:\/\/linked.data.gov.au\/def\/gnaf#Locality<\/a><\/em> class items<\/h2>'
    ), 'GNAF Locality Register reg view html failed'


def test_gnaf_locality_register_reg_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_view=reg&_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    ),' GNAF Locality Register reg view rdf turtle qsa failed'


def test_gnaf_locality_register_reg_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/?_view=reg',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a <http:\/\/linked.data.gov.au\/def\/gnaf#Locality> ;'
    ),' GNAF Locality Register reg view rdf turtle accept header failed'


def test_gnaf_locality_198023_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023',
        None,
        r'<td><code>Argoon<\/code><\/td>'
    ), 'GNAF Locality instance 198023 html failed'


def test_gnaf_locality_198023_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a gnaf:Locality ;'
    ), 'GNAF Locality instance 198023 rdf turtle qsa failed'


def test_gnaf_locality_198023_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a gnaf:Locality ;'
    ), 'GNAF Locality instance 198023 rdf turtle accept header failed'


def test_gnaf_locality_198023_alternates_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=alternates&_format=text/html',
        None,
        r'<h3>Instance <a href="http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023">http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023<\/a><\/h3>'
    ), 'GNAF Locality instance 198023 alternates view html failed'


def test_gnaf_locality_198023_alternates_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=alternates&_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> alt:hasDefaultView'
    ), 'GNAF Locality instance 198023 alternates view rdf turtle qsa failed'


def test_gnaf_locality_198023_alternates_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=alternates',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> alt:hasDefaultView'
    ), 'GNAF Locality instance 198023 alternates view rdf turtle accept header failed'


def test_gnaf_locality_198023_gnaf_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=gnaf&_format=text/html',
        None,
        r'<a href="\/locality\/198023\?_view=alternates">'
    ), 'GNAF Locality instance 198023 gnaf view html failed'


def test_gnaf_locality_198023_gnaf_view_rdf_turtle_qsa():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=gnaf&_format=text/turtle',
        None,
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a gnaf:Locality ;'
    ), 'GNAF Locality instance 198023 gnaf view rdf turtle qsa failed'


def test_gnaf_locality_198023_gnaf_view_rdf_turtle_accept_header():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=gnaf',
        {'Accept': 'text/turtle'},
        r'<http:\/\/linked.data.gov.au\/dataset\/gnaf\/locality\/198023> a gnaf:Locality ;'
    ), 'GNAF Locality instance 198023 gnaf view rdf turtle accept header failed'


def test_gnaf_locality_198023_dct_view_html():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=dct&_format=text/html',
        None,
        r'<a href="\/locality\/198023\?_view=alternates">'
    ), 'GNAF Locality instance 198023 dct view html failed'


@pytest.mark.skip('GNAF Locality instance 198023 dct view rdf turtle qsa not yet implemented')
def test_gnaf_locality_198023_dct_view_rdf_turtle_():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=dct&_format=text/turtle',
        None,
        None #TODO
    ), 'GNAF Locality instance 198023 dct view rdf turtle qsa failed'


@pytest.mark.skip('GNAF Locality instance 198023 dct view rdf turtle accept header not yet implemented')
def test_gnaf_locality_198023_dct_view_rdf_turtle_():
    assert valid_endpoint_content(
        f'{SYSTEM_URI}/locality/198023?_view=dct',
        None,
        None #TODO
    ), 'GNAF Locality instance 198023 dct view rdf turtle accept header failed'


if __name__ == '__main__':
    pass

