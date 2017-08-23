from .renderer import Renderer
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

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='gnaf'):
        if view == 'gnaf':
            address_string = None
            # make a human-readable address
            s = sql.SQL('''SELECT 
                        street_locality_pid, 
                        locality_pid, 
                        CAST(number_first AS text), 
                        street_name, 
                        street_type_code, 
                        locality_name, 
                        state_abbreviation, 
                        postcode 
                    FROM gnaf.address_view 
                    WHERE address_detail_pid = {}''') \
                .format(sql.Literal(self.id))

            try:
                connect_str = "host='{}' dbname='{}' user='{}' password='{}'" \
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
                    address_string = '{} {} {}, {}, {} {}'\
                        .format(row[2], row[3].title(), row[4].title(), row[5].title(), row[6], row[7])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_address_gnaf.html',
                address_string=address_string
            )

        elif view == 'ISO19160':
            view_html = render_template(
                'class_address_ISO19160.html',
            )

        elif view == 'dct':
            s = sql.SQL('''SELECT 
                         street_locality_pid, 
                         locality_pid, 
                         CAST(number_first AS text), 
                         street_name, 
                         street_type_code, 
                         locality_name, 
                         state_abbreviation, 
                         postcode,
                         longitude,
                         latitude
                     FROM gnaf.address_view 
                     WHERE address_detail_pid = {}''') \
                .format(sql.Literal(self.id))

            try:
                connect_str = "host='{}' dbname='{}' user='{}' password='{}'" \
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
                for record in cursor:
                    address_string = '{} {} {}, {}, {} {}' \
                        .format(record[2], record[3].title(), record[4].title(), record[5].title(), record[6], record[7])
                    geometry_wkt = 'SRID=8311;POINT({} {})'.format(record[8], record[9])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_address_dct.html',
                identifier=self.id,
                title='Address ' + self.id,
                description=address_string,
                coverage=geometry_wkt,
                source='G-NAF, 2016',
                type='Address'
            )

        return render_template(
            'class_address.html',
            view_html=view_html,
            address_id=self.id,
            address_uri=self.uri,
        )

    def export_rdf(self, view='ISO19160', format='text/turtle'):
        g = Graph()
        a = URIRef(self.uri)

        if view == 'ISO19160':
            # get the components from the DB needed for ISO19160
            s = sql.SQL('''SELECT 
                        street_locality_pid, 
                        locality_pid, 
                        CAST(number_first AS text), 
                        street_name, 
                        street_type_code, 
                        locality_name, 
                        state_abbreviation, 
                        postcode,
                        longitude,
                        latitude
                    FROM gnaf.address_view 
                    WHERE address_detail_pid = {}''') \
                .format(sql.Literal(self.id))

            try:
                connect_str = "host='{}' dbname='{}' user='{}' password='{}'" \
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
                for record in cursor:
                    ac_street_value = '{} {} {}'.format(record[2], record[3].title(), record[4].title())
                    ac_locality_value = record[5].title()
                    ac_state_value = record[6]
                    ac_postcode_value = record[7]
                    geometry_wkt = 'SRID=8311;POINT({} {})'.format(record[8], record[9])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            AddressComponentTypeUriBase = 'http://def.isotc211.org/iso19160/-1/2015/Address/code/AddressComponentType/'
            AddressPositionTypeUriBase = 'http://def.isotc211.org/iso19160/-1/2015/Address/code/AddressPositionType/'

            ISO = Namespace('http://def.isotc211.org/iso19160/-1/2015/Address#')
            g.bind('iso19160', ISO)

            GEO = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geo', GEO)

            g.add((a, RDF.type, ISO.Address))

            ac_street = BNode()
            g.add((ac_street, RDF.type, ISO.AddressComponent))
            g.add((ac_street, ISO.valueInformation, Literal(ac_street_value, datatype=XSD.string)))
            g.add((ac_street, ISO.type, URIRef(AddressComponentTypeUriBase + 'thoroughfareName')))
            g.add((a, ISO.addressComponent, ac_street))

            ac_locality = BNode()
            g.add((ac_locality, RDF.type, ISO.AddressComponent))
            g.add((ac_locality, ISO.valueInformation, Literal(ac_locality_value, datatype=XSD.string)))
            g.add((ac_locality, ISO.type, URIRef(AddressComponentTypeUriBase + 'locality')))
            g.add((a, ISO.addressComponent, ac_locality))

            ac_state = BNode()
            g.add((ac_state, RDF.type, ISO.AddressComponent))
            g.add((ac_state, ISO.valueInformation, Literal(ac_state_value, datatype=XSD.string)))
            g.add((ac_state, ISO.type, URIRef(AddressComponentTypeUriBase + 'state')))
            g.add((a, ISO.addressComponent, ac_state))

            ac_postcode = BNode()
            g.add((ac_postcode, RDF.type, ISO.AddressComponent))
            g.add((ac_postcode, ISO.valueInformation, Literal(ac_postcode_value, datatype=XSD.string)))
            g.add((ac_postcode, ISO.type, URIRef(AddressComponentTypeUriBase + 'postcode')))
            g.add((a, ISO.addressComponent, ac_postcode))

            geometry = BNode()
            g.add((geometry, RDF.type, GEO.Geometry))
            g.add((geometry, GEO.asWKT, Literal(geometry_wkt, datatype=GEO.wktLiteral)))

            position_geometry = BNode()
            g.add((position_geometry, RDF.type, ISO.GM_Object))
            g.add((position_geometry, GEO.hasGeometry, geometry))

            position = BNode()
            g.add((position, RDF.type, ISO.AddressPosition))
            g.add((position, ISO.geometry, position_geometry))
            g.add((position, ISO.type, URIRef(AddressPositionTypeUriBase + 'centroid')))
            g.add((a, ISO.position, position))

        elif view == 'gnaf':
            pass

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))
