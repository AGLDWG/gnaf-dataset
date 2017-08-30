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
        self.alias_address_ids = []
        self.principal_address_ids = []
        self.primary_address_ids = []
        self.secondary_address_ids = []
        self.mesh_block_2011s = []
        self.mesh_block_2016s = []

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
                        b.street_locality_pid, 
                        b.locality_pid, 
                        CAST(b.number_first AS text), 
                        a.street_name, 
                        a.street_type_code, 
                        a.locality_name, 
                        a.state_abbreviation, 
                        b.postcode ,
                        a.latitude,
                        a.longitude,
                        a.geocode_type,
                        CAST(b.confidence AS text),
                        CAST(b.date_created AS text),
                        CAST(b.date_last_modified AS text),
                        CAST(b.date_retired AS text),
                        b.building_name,
                        b.lot_number_prefix,
                        b.lot_number,
                        b.lot_number_suffix,
                        b.flat_type_code,
                        b.flat_number_prefix,
                        CAST(b.flat_number AS text),
                        b.flat_number_suffix,
                        b.level_type_code,
                        b.level_number_prefix,
                        CAST(b.level_number AS text),
                        b.level_number_suffix,
                        b.number_first_prefix,
                        b.number_first_suffix,
                        b.number_last_prefix,
                        CAST(b.number_last AS text),
                        b.number_last_suffix,
                        b.alias_principal,
                        b.legal_parcel_id,
                        b.address_site_pid,
                        b.level_geocoded_code,
                        b.property_pid,
                        b.primary_secondary                        
                    FROM {dbschema}.address_view a INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
                    WHERE a.address_detail_pid = {id}''') \
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
                    street_locality_pid = row[0]
                    locality_pid = row[1]
                    street_number_1 = row[2]
                    street_name = row[3].title()
                    street_type = row[4].title()
                    locality_name = row[5].title()
                    state_territory = row[6]
                    postcode = row[7]
                    latitude = row[8]
                    longitude = row[9]
                    geocode_type = row[10].title()
                    confidence = row[11]
                    date_created = row[12]
                    date_last_modified = row[13]
                    date_retired = row[14]
                    building_name = row[15]
                    lot_number_prefix = row[16]
                    lot_number = row[17]
                    lot_number_suffix = row[18]
                    flat_type_code = row[19]
                    flat_number_prefix = row[20]
                    flat_number = row[21]
                    flat_number_suffix = row[22]
                    level_type_code = row[23]
                    level_number_prefix = row[24]
                    level_number = row[25]
                    level_number_suffix = row[26]
                    number_first_prefix = row[27]
                    number_first_suffix = row[28]
                    number_last_prefix = row[29]
                    number_last = row[30]
                    number_last_suffix = row[31]
                    alias_principal = row[32]
                    legal_parcel_id = row[33]
                    address_site_pid = row[34]
                    level_geocoded_code = row[35]
                    property_pid = row[36]
                    primary_secondary = row[37]
                    geometry_wkt = 'SRID=8311;POINT({} {})'.format(latitude, longitude)
                    address_string = '{} {} {}, {}, {} {}'\
                        .format(street_number_1, street_name, street_type, locality_name, state_territory, postcode)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            # get a list of aliasIds from the address_alias table
            s2 = sql.SQL('''SELECT 
                        alias_pid,
                        alias_type_code                
                    FROM {dbschema}.address_alias
                    WHERE principal_pid = {id}''') \
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
                    self.alias_address_ids.append(row[0])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            # get a list of principalIds from the address_alias table
            s3 = sql.SQL('''SELECT 
                        principal_pid,
                        alias_type_code                
                    FROM {dbschema}.address_alias
                    WHERE alias_pid = {id}''') \
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
                cursor.execute(s3)
                rows = cursor.fetchall()
                for row in rows:
                    self.principal_address_ids.append(row[0])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_address_gnaf.html',
                address_string=address_string,
                address_detail_pid=self.id,
                street_number_1=street_number_1,
                street_name=street_name,
                street_type=street_type,
                locality_name=locality_name,
                state_territory=state_territory,
                postcode=postcode,
                latitude=latitude,
                longitude=longitude,
                geocode_type=geocode_type,
                confidence=confidence,
                geometry_wkt=geometry_wkt,
                date_created=date_created,
                date_last_modified=date_last_modified,
                date_retired=date_retired,
                building_name=building_name,
                lot_number_prefix=lot_number_prefix,
                lot_number=lot_number,
                lot_number_suffix=lot_number_suffix,
                flat_type_code=flat_type_code,
                flat_number_prefix=flat_number_prefix,
                flat_number=flat_number,
                flat_number_suffix=flat_number_suffix,
                level_type_code=level_type_code,
                level_number_prefix=level_number_prefix,
                level_number=level_number,
                level_number_suffix=level_number_suffix,
                number_first_prefix=number_first_prefix,
                number_first_suffix=number_first_suffix,
                number_last_prefix=number_last_prefix,
                number_last=number_last,
                number_last_suffix=number_last_suffix,
                alias_principal=alias_principal,
                legal_parcel_id=legal_parcel_id,
                address_site_pid=address_site_pid,
                level_geocoded_code=level_geocoded_code,
                property_pid=property_pid,
                primary_secondary=primary_secondary,
                street_locality_pid=street_locality_pid,
                locality_pid=locality_pid,
                alias_address_ids = self.alias_address_ids,
                principal_address_ids = self.principal_address_ids
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
                     FROM {dbschema}.address_view 
                     WHERE address_detail_pid = {id}''') \
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
                    FROM {dbschema}.address_view 
                    WHERE address_detail_pid = {id}''') \
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
