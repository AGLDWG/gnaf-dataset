from .renderer import Renderer
from datetime import datetime
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi.ldapi import LDAPI
import psycopg2
from psycopg2 import sql


class AddressRenderer(Renderer):
    """
    This class represents an Address and methods in this class allow an Address to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id):
        # TODO: why doesn't this super thing work?
        # super(AddressRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_ADDRESS_INSTANCE_BASE + id
        # TODO: actually load data from G-NAF DB
        # SELECT * FROM gnaf.address_view WHERE address_detail_pid = 'GAACT714892579';

    def render(self, view, mimetype):
        if view == 'gnaf':
            if mimetype == 'text/html':
                return self.export_html(model_view=view)
            else:
                return Response(self.export_rdf(view, mimetype), mimetype=mimetype)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, model_view='gnaf'):
        self.address_string = None
        # make a human-readable address
        s = sql.SQL('''SELECT 
                    street_locality_pid, 
                    locality_pid, 
                    CAST(number_first AS text), 
                    street_name, street_type_code, 
                    locality_name, 
                    state_abbreviation, 
                    postcode 
                FROM gnaf.address_view 
                WHERE address_detail_pid = {}''')\
            .format(sql.Literal(self.id))

        try:
            connect_str = "host='{}' dbname='{}' user='{}' password='{}'"\
                .format(
                    config.DB_HOST,
                    config.DB_DBNAME,
                    config.DB_USR,
                    config.DB_PWD
                )
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s)
            rows = cursor.fetchall()
            for row in rows:
                self.address_string = '{} {} {}, {}, {} {}'.format(row[2], row[3].title(), row[4].title(), row[5].title(),
                                                              row[6], row[7])
        except Exception as e:
            print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
            print(e)
        if model_view == 'gnaf':
            view_html = render_template(
                'class_address_landingpage.html',
                address_id=self.uri,
                address_string=self.address_string
            )

        # TODO: generalise this to the wrapper template using the view_html template from above within
        return render_template(
            'class_address.html',
            view_html=view_html,
            address_id=self.id
        )

    def export_rdf(self):
        pass