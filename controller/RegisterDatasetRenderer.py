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
        pass

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
