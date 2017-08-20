from .renderer import Renderer
from datetime import datetime
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config
from _ldapi.ldapi import LDAPI


class AddressRenderer(Renderer):
    """
    This class represents an Address and methods in this class allow an Address to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id):
        super(AddressRenderer, self).__init__(id)
        # TODO: actually load data from G-NAF DB
        # SELECT * FROM gnaf.address_view WHERE address_detail_pid = 'GAACT714892579';

    def render(self, view, mimetype):
        # TODO: actually render stuff
        pass
