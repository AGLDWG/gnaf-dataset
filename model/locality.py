from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
import psycopg2
from psycopg2 import sql


class LocalityRenderer(Renderer):
    """
    This class represents a Locality and methods in this class allow a Locality to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id):
        # TODO: why doesn't this super thing work?
        # super(LocalityRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_LOCALITY_INSTANCE_BASE + id
        self.locality_aliases = dict()
        self.locality_neighbours = dict()

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='gnaf'):
        if view == 'gnaf':
            # connect to DB
            cursor = config.get_db_cursor()

            locality_name = None
            # make a human-readable street
            s = sql.SQL('''SELECT 
                        locality_name, 
                        latitude,
                        longitude,
                        geocode_type,
                        locality_pid,
                        state_pid
                    FROM {dbschema}.locality_view
                    WHERE locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            cursor.execute(s)
            rows = cursor.fetchall()
            for row in rows:
                r = config.reg(cursor, row)
                locality_name = r.locality_name.title()
                latitude = r.latitude
                longitude = r.longitude
                geocode_type = r.geocode_type.title()
                locality_pid = r.locality_pid
                state_pid = r.state_pid
                geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(
                    latitude,
                    longitude
                )

            # get a list of localityAliasIds from the locality_alias table
            s2 = sql.SQL('''SELECT 
                        locality_alias_pid,
                        "name"           
                    FROM {dbschema}.locality_alias
                    WHERE locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s2)
            rows = cursor.fetchall()
            for row in rows:
                r = config.reg(cursor, row)
                self.locality_aliases[r.locality_alias_pid] = r.name.title()

            # get a list of localityNeighbourIds from the locality_alias table
            s2 = sql.SQL('''SELECT 
                        a.neighbour_locality_pid,
                        b.locality_name                
                    FROM {dbschema}.locality_neighbour a
                    INNER JOIN {dbschema}.locality_view b ON a.neighbour_locality_pid = b.locality_pid
                    WHERE a.locality_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s2)
            rows = cursor.fetchall()
            for row in rows:
                r = config.reg(cursor, row)
                self.locality_neighbours[r.neighbour_locality_pid] = r.locality_name.title()

            view_html = render_template(
                'class_locality_gnaf.html',
                locality_name=locality_name,
                latitude=latitude,
                longitude=longitude,
                geocode_type=geocode_type,
                geometry_wkt=geometry_wkt,
                locality_pid=locality_pid,
                state_pid=state_pid,
                locality_aliases=self.locality_aliases,
                locality_neighbours=self.locality_neighbours
            )

        elif view == 'ISO19160':
            view_html = render_template(
                'class_locality_ISO19160.html',
            )

        elif view == 'dct':
            s = sql.SQL('''SELECT 
                        locality_name, 
                        latitude,
                        longitude,
                        geocode_type,
                        locality_pid,
                        state_pid
                    FROM {dbschema}.locality_view
                    WHERE locality_pid = {id}''') \
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
                    locality_name = record[0]
                    latitude = record[1]
                    longitude = record[2]
                    geocode_type = record[3].title()
                    locality_pid = record[4]
                    state_pid = record[5]
                    geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(latitude, longitude)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_locality_dct.html',
                identifier=self.id,
                title='Locality ' + self.id,
                description=locality_name,
                coverage=geometry_wkt,
                source='G-NAF, 2016',
                type='Locality'
            )

        return render_template(
            'class_locality.html',
            view_html=view_html,
            locality_id=self.id,
            locality_uri=self.uri,
        )

    def export_rdf(self, view='ISO19160', format='text/turtle'):
        g = Graph()
        a = URIRef(self.uri)

        if view == 'ISO19160':
            # get the components from the DB needed for ISO19160
            s = sql.SQL('''SELECT 
                        locality_name, 
                        latitude,
                        longitude,
                        geocode_type,
                        locality_pid,
                        state_pid
                    FROM {dbschema}.locality_view
                    WHERE locality_pid = {id}''') \
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
                    ac_locality_value = record[0].title()
                    geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(record[1], record[2])
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

            ac_locality = BNode()
            g.add((ac_locality, RDF.type, ISO.AddressComponent))
            g.add((ac_locality, ISO.valueInformation, Literal(ac_locality_value, datatype=XSD.string)))
            g.add((ac_locality, ISO.type, URIRef(AddressComponentTypeUriBase + 'locality')))
            g.add((a, ISO.addressComponent, ac_locality))

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
