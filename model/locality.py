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

    def __init__(self, id, db_cursor=None):
        # TODO: why doesn't this super thing work?
        # super(LocalityRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_LOCALITY_INSTANCE_BASE + id

        # DB connection
        if db_cursor is not None:
            self.cursor = db_cursor
        else:
            self.cursor = config.get_db_cursor()

        self.locality_name = None
        self.latitude = None
        self.longitude = None
        self.date_created = None
        self.date_retired = None
        self.geocode_type = None
        self.geometry_wkt = None
        self.state_pid = None
        self.alias_localities = []
        self.locality_neighbours = dict()

        # get data from DB
        s = sql.SQL('''SELECT 
                            locality_name, 
                            l.date_created,
                            l.date_retired,
                            primary_postcode,
                            latitude,
                            longitude,
                            s.uri AS state_uri, 
                            s.prefLabel AS state_label
                        FROM gnaf.locality l
                        INNER JOIN gnaf.locality_point lp on l.locality_pid = lp.locality_pid
                        LEFT JOIN codes.state s ON CAST(l.state_pid AS text) = s.code
                        WHERE l.locality_pid = {id}''') \
            .format(id=sql.Literal(self.id))

        self.cursor.execute(s)
        rows = self.cursor.fetchall()
        for row in rows:
            r = config.reg(self.cursor, row)
            self.locality_name = r.locality_name.title()
            self.latitude = r.latitude
            self.longitude = r.longitude
            self.date_created = r.date_created
            self.date_retired = r.date_retired
            self.state_uri = r.state_uri
            self.state_label = r.state_label
            if self.latitude is not None and self.longitude is not None:
                self.geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(
                    self.latitude,
                    self.longitude
                )

        s2 = sql.SQL('''SELECT locality_alias_pid, name, uri, prefLabel 
                        FROM gnaf.locality_alias 
                        LEFT JOIN codes.alias a ON gnaf.locality_alias.alias_type_code = a.code 
                        WHERE locality_pid = {id}''') \
            .format(id=sql.Literal(self.id))

        # get just IDs, ordered, from the address_detail table, paginated by class init args
        self.cursor.execute(s2)
        rows = self.cursor.fetchall()
        for row in rows:
            r = config.reg(self.cursor, row)
            self.alias_localities.append(r.name.title())

        # get a list of localityNeighbourIds from the locality_alias table
        s3 = sql.SQL('''SELECT 
                    a.neighbour_locality_pid,
                    b.locality_name                
                FROM gnaf.locality_neighbour a
                INNER JOIN gnaf.locality_view b ON a.neighbour_locality_pid = b.locality_pid
                WHERE a.locality_pid = {id}''') \
            .format(id=sql.Literal(self.id))
        # get just IDs, ordered, from the address_detail table, paginated by class init args
        self.cursor.execute(s3)
        rows = self.cursor.fetchall()
        for row in rows:
            r = config.reg(self.cursor, row)
            self.locality_neighbours[r.neighbour_locality_pid] = r.locality_name.title()

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='gnaf'):
        if view == 'gnaf':
            view_html = render_template(
                'class_locality_gnaf.html',
                locality_name=self.locality_name,
                latitude=self.latitude,
                longitude=self.longitude,
                geocode_type=self.geocode_type,
                geometry_wkt=make_wkt_literal(self.latitude, self.longitude),
                state_uri=self.state_uri,
                state_label=self.state_label,
                geocode_uri='http://gnafld.net/def/gnaf/code/GeocodeTypes#Locality',
                geocode_label='Locality',
                alias_localities=self.alias_localities,
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
                    FROM gnaf.locality_view
                    WHERE locality_pid = {id}''') \
                .format(id=sql.Literal(self.id))

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

    def export_rdf(self, view='gnaf', format='text/turtle'):
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
                    FROM gnaf.locality_view
                    WHERE locality_pid = {id}''') \
                .format(id=sql.Literal(self.id))

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
            RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
            g.bind('rdfs', RDFS)

            GNAF = Namespace('http://gnafld.net/def/gnaf#')
            g.bind('gnaf', GNAF)

            GEO = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geo', GEO)

            PROV = Namespace('http://www.w3.org/ns/prov#')
            g.bind('prov', PROV)

            DCT = Namespace('http://purl.org/dc/terms/')
            g.bind('dct', DCT)

            l = URIRef(self.uri)

            # RDF: declare Address instance
            g.add((l, RDF.type, GNAF.Locality))
            g.add((l, GNAF.hasName, Literal(self.locality_name, datatype=XSD.string)))
            g.add((a, GNAF.hasDateCreated, Literal(self.date_created, datatype=XSD.date)))
            if self.date_retired is not None:
                g.add((a, GNAF.hasDateRetired, Literal(self.date_retired, datatype=XSD.date)))
            g.add((l, GNAF.hasState, URIRef(self.state_uri)))
            # RDF: geometry
            geocode = BNode()
            g.add((geocode, RDF.type, GNAF.Geocode))
            g.add((geocode, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/GeocodeTypes#Locality')))
            g.add((geocode, RDFS.label, Literal('Locality', datatype=XSD.string)))
            g.add((geocode, GEO.asWKT,
                   Literal(make_wkt_literal(self.longitude, self.latitude), datatype=GEO.wktLiteral)))
            g.add((a, GEO.hasGeometry, geocode))

            if hasattr(self, 'alias_localities'):
                for al in self.alias_localities:
                    a = BNode()
                    g.add((a, RDF.type, GNAF.Alias))
                    g.add((URIRef(self.uri), GNAF.hasAlias, a))
                    g.add((a, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/AliasTypes#Synonym')))
                    g.add((a, RDFS.label, Literal(al, datatype=XSD.string)))

            if hasattr(self, 'locality_neighbours'):
                for k, v in self.locality_neighbours.items():
                    g.add((l, GNAF.hasNeighbour, URIRef(config.URI_LOCALITY_INSTANCE_BASE + k)))

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))


def make_wkt_literal(longitude, latitude):
    return '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(
        longitude, latitude
    )

