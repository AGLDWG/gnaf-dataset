import pyldapi
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, XSD, BNode, OWL
import _config as config


class RegisterDatasetRenderer(pyldapi.RegisterOfRegistersRenderer):
    """
    Specialised implementation of the RegisterOfRegistersRenderer for adding DCAT v2 properties to the display of
    a Register of Register which is expected to a whole datasets
    """
    def __init__(self, request, uri, label, comment, rofr_file_path, *args,
                 super_register=None, **kwargs):

        # push RofR properties up to the RofR constructor
        super().__init__(
            request, uri, label, comment, rofr_file_path, *args, ['http://purl.org/linked-data/registry#Register'],
            super_register=super_register, **kwargs
        )

    def _generate_reg_view_rdf(self):
        # first it does all the RofR things, automatically
        # now we add DCAT things
        g = super(pyldapi.RegisterOfRegistersRenderer, self)._generate_reg_view_rdf()
        # REG = Namespace('http://purl.org/linked-data/registry#')
        # for uri_str, cics in self.subregister_cics.items():
        #     uri = URIRef(uri_str)
        #     for cic in cics:
        #         g.add((uri, REG.containedItemClass, cic))
        DCAT = Namespace('http://www.w3.org/ns/dcat#')
        g.bind('dcat', DCAT)
        FOAF = Namespace('http://xmlns.com/foaf/0.1/')
        g.bind('foaf', FOAF)
        DCT = Namespace('http://purl.org/dc/terms/')
        g.bind('dct', DCT)
        VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
        g.bind('vcard', VCARD)
        # PROV = Namespace('http://www.w3.org/ns/prov-o#')
        # g.bind('prov', PROV)

        #
        #   Dataset - https://w3c.github.io/dxwg/dcat/#Class:Dataset
        #
        dataset_uri = URIRef('https://data.gov.au/dataset/geocoded-national-address-file-g-naf')

        #
        #   Distributions - https://w3c.github.io/dxwg/dcat/#Class:Data_Distribution_Service
        #
        vcard2 = BNode()
        g.add((vcard2, RDF.type, VCARD.Individual))
        g.add((vcard2, VCARD.fn, Literal("Nicholas Car")))
        g.add((vcard2, VCARD.hasEmail, URIRef('nicholas.car@csiro.au')))
        phone = BNode()
        g.add((phone, RDF.type, VCARD.Home))
        g.add((phone, VCARD.hasValue, URIRef('tel:+61738335632')))
        g.add((vcard2, VCARD.hasTelephone, phone))

        dist_service = URIRef('http://linked.data.gov.au/dataset/gnaf/sparql')
        g.add((dist_service, RDF.type, DCAT.DataDistributionService))
        g.add((dist_service, DCT.title, Literal('GNAF SPARQL Service')))
        g.add((dist_service, DCT.description, Literal('A SPARQL 1.1 service accessing all of the content of the GNAF in RDF')))
        g.add((dist_service, DCAT.servesDataset, dataset_uri))
        g.add((dist_service, DCAT.endpointURL, dist_service))
        g.add((dist_service, DCAT.endpointDescription, URIRef('http://linked.data.gov.au/dataset/gnaf/sparql.ttl')))
        g.add((dist_service, DCAT.license, URIRef('https://data.gov.au/dataset/19432f89-dc3a-4ef3-b943-5326ef1dbecc/resource/09f74802-08b1-4214-a6ea-3591b2753d30')))
        g.add((dist_service, DCAT.contactPoint, vcard2))

        dist_service2 = URIRef(self.uri)
        g.add((dist_service2, OWL.sameAs, URIRef('http://linked.data.gov.au/dataset/gnaf')))
        g.add((dist_service2, RDF.type, DCAT.DataDistributionService))
        g.add((dist_service2, DCT.title, Literal('GNAF Linked Data API Service')))
        g.add((dist_service2, DCT.description, Literal('A Linked Data API accessing all of the content of the GNAF in RDF & HTML')))
        g.add((dist_service2, DCAT.servesDataset, dataset_uri))
        g.add((dist_service2, DCAT.endpointURL, dist_service2))
        g.add((dist_service2, DCAT.endpointDescription, URIRef('http://linked.data.gov.au/dataset/gnaf.ttl')))
        g.add((dist_service2, DCAT.license, URIRef('https://data.gov.au/dataset/19432f89-dc3a-4ef3-b943-5326ef1dbecc/resource/09f74802-08b1-4214-a6ea-3591b2753d30')))
        g.add((dist_service2, DCAT.contactPoint, vcard2))

        # clean out any leftover properties
        g.remove((dist_service2, RDFS.label, Literal(self.label, datatype=XSD.string)))
        g.remove((dist_service2, RDFS.comment, Literal(self.comment, datatype=XSD.string)))

        return g

    def _generate_dcat_view_rdf(self):
        with open(config.APP_DIR + '/dcat.ttl', 'r') as f:
            return f.read()

    def _generate_void_view_rdf(self):
        with open(config.APP_DIR + '/void.ttl', 'r') as f:
            return f.read()

    def _generate_all_view_rdf(self):
        g = Graph()
        g.parse(file=config.APP_DIR + '/dcat.ttl', format='turtle')
        g.parse(file=config.APP_DIR + '/rofr.ttl', format='turtle')
        g.parse(file=config.APP_DIR + '/void.ttl', format='turtle')

        return g.serialize(format='turtle')
