from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi.ldapi import LDAPI
import psycopg2
from psycopg2 import sql


class StreetRenderer(Renderer):
    """
    This class represents a Street and methods in this class allow a Street to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id):
        # TODO: why doesn't this super thing work?
        # super(StreetRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_STREET_INSTANCE_BASE + id
        self.street_locality_alias_pids = []

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='gnaf'):
        if view == 'gnaf':
            street_string = None
            # make a human-readable street
            s = sql.SQL('''SELECT 
                        street_name, 
                        street_type_code, 
                        street_suffix_code,
                        latitude,
                        longitude,
                        geocode_type,
                        locality_pid
                    FROM {dbschema}.street_view
                    WHERE street_locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

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
                    street_name = row[0]
                    street_type = row[1]
                    street_suffix = row[2]
                    latitude = row[3]
                    longitude = row[4]
                    geocode_type = row[5].title()
                    locality_pid = row[6]
                    geometry_wkt = 'SRID=8311;POINT({} {})'.format(latitude, longitude)
                    street_string = '{} {} {}'\
                        .format(street_name, street_type, street_suffix)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            # get a list of addressSiteGeocodeIds from the address_site_geocode table
            s2 = sql.SQL('''SELECT 
                        street_locality_alias_pid                
                    FROM {dbschema}.street_locality_alias
                    WHERE street_locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

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
                cursor.execute(s2)
                rows = cursor.fetchall()
                for row in rows:
                    self.street_locality_alias_pids.append(row[0])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_street_gnaf.html',
                street_string=street_string,
                street_locality_pid=self.id,
                street_name=street_name,
                street_type=street_type,
                street_suffix=street_suffix,
                latitude=latitude,
                longitude=longitude,
                geocode_type=geocode_type,
                geometry_wkt=geometry_wkt,
                locality_pid=locality_pid,
                street_locality_alias_ids=self.street_locality_alias_pids
            )

        elif view == 'ISO19160':
            view_html = render_template(
                'class_street_ISO19160.html',
            )

        elif view == 'dct':
            s = sql.SQL('''SELECT 
                        street_name, 
                        street_type_code, 
                        street_suffix_code,
                        latitude,
                        longitude,
                        geocode_type,
                        locality_pid
                    FROM {dbschema}.street_view
                    WHERE street_locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

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
                    street_name = record[0]
                    street_type = record[1]
                    street_suffix = record[2]
                    latitude = record[3]
                    longitude = record[4]
                    geocode_type = record[5].title()
                    locality_pid = record[6]
                    geometry_wkt = 'SRID=8311;POINT({} {})'.format(latitude, longitude)
                    street_string = '{} {} {}'\
                        .format(street_name, street_type, street_suffix)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_street_dct.html',
                identifier=self.id,
                title='Street ' + self.id,
                description=street_string,
                coverage=geometry_wkt,
                source='G-NAF, 2016',
                type='Street'
            )

        return render_template(
            'class_street.html',
            view_html=view_html,
            street_id=self.id,
            street_uri=self.uri,
        )

    def export_rdf(self, view='ISO19160', format='text/turtle'):
        g = Graph()
        a = URIRef(self.uri)

        if view == 'ISO19160':
            # get the components from the DB needed for ISO19160
            s = sql.SQL('''SELECT 
                        street_name, 
                        street_type_code, 
                        street_suffix_code,
                        latitude,
                        longitude,
                        geocode_type,
                        locality_pid
                    FROM {dbschema}.street_view
                    WHERE street_locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

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
                    ac_street_value = record[0].title()
                    if(record[1] != None):
                        ac_street_value += ' {}'.format(record[1].title())
                    if(record[2] != None):
                        ac_street_value += ' {}'.format(record[2].title())
                    geometry_wkt = 'SRID=8311;POINT({} {})'.format(record[3], record[4])
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
