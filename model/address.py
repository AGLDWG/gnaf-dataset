from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
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
        self.alias_addresses = dict()
        self.principal_addresses = dict()
        self.primary_addresses = dict()
        self.secondary_addresses = dict()
        self.mesh_block_2011s = []
        self.mesh_block_2016s = []

    def format_address(self,
                       level_type_code=None, level_number_prefix=None, level_number=None, level_number_suffix=None,
                       flat_type_code=None, flat_number_prefix=None, flat_number=None, flat_number_suffix=None,
                       number_first_prefix=None, number_first=None, number_first_suffix=None,
                       number_last_prefix=None, number_last=None, number_last_suffix=None,
                       building=None, lot_number_prefix=None, lot_number=None, lot_number_suffix=None,
                       street_name=None, street_type=None, street_suffix_code=None,
                       locality=None, state_territory=None, postcode=None):
        street_string = '{}{}'.format(street_name, ' ' + street_type.title() if street_type is not None else '')
        address_string = ''
        if locality is None:
            address_string = street_string
        else:
            flatNum = '{}{}{}'.format(flat_number_prefix if flat_number_prefix is not None else '',
                                      flat_number if flat_number is not None else '',
                                      flat_number_suffix if flat_number_suffix is not None else '')
            levelNum = '{}{}{}'.format(level_number_prefix if level_number_prefix is not None else '',
                                       level_number if level_number is not None else '',
                                       level_number_suffix if level_number_suffix is not None else '')
            lotNum = '{}{}{}'.format(lot_number_prefix if lot_number_prefix is not None else '',
                                     lot_number if lot_number is not None else '',
                                     lot_number_suffix if lot_number_suffix is not None else '')
            num1 = '{}{}{}'.format(number_first_prefix if number_first_prefix is not None else '',
                                   number_first if number_first is not None else '',
                                   number_first_suffix if number_first_suffix is not None else '')
            num2 = '{}{}{}'.format(number_last_prefix if number_last_prefix is not None else '',
                                   number_last if number_last is not None else '',
                                   number_last_suffix if number_last_suffix is not None else '')
            if level_type_code is not None:
                address_string += level_type_code.title() + ' '
            if levelNum != '':
                address_string += levelNum + ' '
            if flatNum != '':
                address_string += '{flattype} {flatnum} '.format(flattype=flat_type_code.title(),
                                                                 flatnum=flatNum) if flat_type_code is not None else flatNum + ' '
            if building is not None:
                address_string += building.title() + ' '
            if num1 != '':
                address_string += num1
                if num2 != '':
                    address_string += '-' + num2
                address_string += ' '
            else:
                address_string += 'LOT {lotnum} '.format(lotnum=lotNum)
            address_string += '{st}, {loc}, {state} {postcode}' \
                .format(st=street_string, loc=locality, state=state_territory, postcode=postcode)
        return address_string, street_string

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        elif format in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_rdf(view, format), mimetype=format)
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def export_html(self, view='gnaf'):
        if view == 'gnaf':
            # initialise all varables in case not found by SQL
            street_locality_pid = None
            locality_pid = None
            street_number_1 = None
            street_name = None
            street_type = None
            locality_name = None
            state_territory = None
            postcode = None
            latitude = None
            longitude = None
            geocode_type = None
            confidence = None
            date_created = None
            date_last_modified = None
            date_retired = None
            building_name = None
            lot_number_prefix = None
            lot_number = None
            lot_number_suffix = None
            flat_type_code = None
            flat_number_prefix = None
            flat_number = None
            flat_number_suffix = None
            level_type_code = None
            level_number_prefix = None
            level_number = None
            level_number_suffix = None
            number_first_prefix = None
            number_first_suffix = None
            number_last_prefix = None
            number_last = None
            number_last_suffix = None
            alias_principal = None
            legal_parcel_id = None
            address_site_pid = None
            level_geocoded_code = None
            property_pid = None
            primary_secondary = None
            geometry_wkt = None

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
                    street_type = row[4]
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
                    geometry_wkt = 'SRID=GDA94;POINT({} {})'.format(latitude, longitude)
            except Exception as e:
                print("DB conn 1 can't connect to DB for query s. Invalid dbname, user or password?")
                print(e)

            this_address_string, this_street_string = self.format_address(
                level_type_code=level_type_code, level_number_prefix=level_number_prefix, level_number=level_number, level_number_suffix=level_number_suffix,
                flat_type_code=flat_type_code, flat_number_prefix=flat_number_prefix, flat_number=flat_number, flat_number_suffix=flat_number_suffix,
                number_first_prefix=number_first_prefix, number_first=street_number_1, number_first_suffix=number_first_suffix,
                number_last_prefix=number_last_prefix, number_last=number_last, number_last_suffix=number_last_suffix,
                building=building_name, lot_number_prefix=lot_number_prefix, lot_number=lot_number, lot_number_suffix=lot_number_suffix,
                street_name=street_name, street_type=street_type,
                locality=locality_name, state_territory=state_territory, postcode=postcode
            )

            # get a list of aliasIds from the address_alias table
            s2 = sql.SQL('''SELECT 
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
                        c.alias_pid,
                        c.alias_type_code                                        
                    FROM 
                        {dbschema}.address_alias c
                          INNER JOIN {dbschema}.address_view a ON c.alias_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
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
                    al_street_locality_pid = row[0]
                    al_locality_pid = row[1]
                    al_street_number_1 = row[2]
                    al_street_name = row[3].title()
                    al_street_type = row[4]
                    al_locality_name = row[5].title()
                    al_state_territory = row[6]
                    al_postcode = row[7]
                    al_latitude = row[8]
                    al_longitude = row[9]
                    al_geocode_type = row[10].title()
                    al_al_confidence = row[11]
                    al_date_created = row[12]
                    al_date_last_modified = row[13]
                    al_date_retired = row[14]
                    al_building_name = row[15]
                    al_lot_number_prefix = row[16]
                    al_lot_number = row[17]
                    al_lot_number_suffix = row[18]
                    al_flat_type_code = row[19]
                    al_flat_number_prefix = row[20]
                    al_flat_number = row[21]
                    al_flat_number_suffix = row[22]
                    al_level_type_code = row[23]
                    al_level_number_prefix = row[24]
                    al_level_number = row[25]
                    al_level_number_suffix = row[26]
                    al_number_first_prefix = row[27]
                    al_number_first_suffix = row[28]
                    al_number_last_prefix = row[29]
                    al_number_last = row[30]
                    al_number_last_suffix = row[31]

                    alias_address_string, alias_street_string = self.format_address(
                        level_type_code=al_level_type_code, level_number_prefix=al_level_number_prefix,
                        level_number=al_level_number, level_number_suffix=al_level_number_suffix,
                        flat_type_code=al_flat_type_code, flat_number_prefix=al_flat_number_prefix, flat_number=al_flat_number,
                        flat_number_suffix=al_flat_number_suffix,
                        number_first_prefix=al_number_first_prefix, number_first=al_street_number_1,
                        number_first_suffix=al_number_first_suffix,
                        number_last_prefix=al_number_last_prefix, number_last=al_number_last,
                        number_last_suffix=al_number_last_suffix,
                        building=al_building_name, lot_number_prefix=al_lot_number_prefix, lot_number=al_lot_number,
                        lot_number_suffix=al_lot_number_suffix,
                        street_name=al_street_name, street_type=al_street_type,
                        locality=al_locality_name, state_territory=al_state_territory, postcode=al_postcode
                    )
                    self.alias_addresses[row[32]] = alias_address_string
            except Exception as e:
                print("DB conn 2, can't connect to DB for query s2. Invalid dbname, user or password?")
                print(e)

            # get a list of principalIds from the address_alias table
            s3 = sql.SQL('''SELECT 
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
                        c.principal_pid,
                        c.alias_type_code                                        
                    FROM 
                        {dbschema}.address_alias c
                          INNER JOIN {dbschema}.address_view a ON c.principal_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
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
                    pc_street_locality_pid = row[0]
                    pc_locality_pid = row[1]
                    pc_street_number_1 = row[2]
                    pc_street_name = row[3].title()
                    pc_street_type = row[4]
                    pc_locality_name = row[5].title()
                    pc_state_territory = row[6]
                    pc_postcode = row[7]
                    pc_latitude = row[8]
                    pc_longitude = row[9]
                    pc_geocode_type = row[10].title()
                    pc_confidence = row[11]
                    pc_date_created = row[12]
                    pc_date_last_modified = row[13]
                    pc_date_retired = row[14]
                    pc_building_name = row[15]
                    pc_lot_number_prefix = row[16]
                    pc_lot_number = row[17]
                    pc_lot_number_suffix = row[18]
                    pc_flat_type_code = row[19]
                    pc_flat_number_prefix = row[20]
                    pc_flat_number = row[21]
                    pc_flat_number_suffix = row[22]
                    pc_level_type_code = row[23]
                    pc_level_number_prefix = row[24]
                    pc_level_number = row[25]
                    pc_level_number_suffix = row[26]
                    pc_number_first_prefix = row[27]
                    pc_number_first_suffix = row[28]
                    pc_number_last_prefix = row[29]
                    pc_number_last = row[30]
                    pc_number_last_suffix = row[31]

                    principal_address_string, principal_street_string = self.format_address(
                        level_type_code=pc_level_type_code, level_number_prefix=pc_level_number_prefix,
                        level_number=pc_level_number, level_number_suffix=pc_level_number_suffix,
                        flat_type_code=pc_flat_type_code, flat_number_prefix=pc_flat_number_prefix, flat_number=pc_flat_number,
                        flat_number_suffix=pc_flat_number_suffix,
                        number_first_prefix=pc_number_first_prefix, number_first=pc_street_number_1,
                        number_first_suffix=pc_number_first_suffix,
                        number_last_prefix=pc_number_last_prefix, number_last=pc_number_last,
                        number_last_suffix=pc_number_last_suffix,
                        building=pc_building_name, lot_number_prefix=pc_lot_number_prefix, lot_number=pc_lot_number,
                        lot_number_suffix=pc_lot_number_suffix,
                        street_name=pc_street_name, street_type=pc_street_type,
                        locality=pc_locality_name, state_territory=pc_state_territory, postcode=pc_postcode
                    )
                    self.principal_addresses[row[32]] = principal_address_string
            except Exception as e:
                print("DB conn 3, can't connect to DB for query s3. Invalid dbname, user or password?")
                print(e)

            # get a list of secondaryIds from the primary_secondary table
            s4 = sql.SQL('''SELECT 
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
                        c.secondary_pid,
                        c.ps_join_type_code                                        
                    FROM 
                        {dbschema}.primary_secondary c
                        INNER JOIN {dbschema}.address_view a ON c.secondary_pid = a.address_detail_pid
                        INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
                    WHERE primary_pid = {id}''') \
                .format(dbschema=sql.Identifier(config.DB_SCHEMA), id=sql.Literal(self.id))

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
                cursor.execute(s4)
                rows = cursor.fetchall()
                for row in rows:
                    sc_street_locality_pid = row[0]
                    sc_locality_pid = row[1]
                    sc_street_number_1 = row[2]
                    sc_street_name = row[3].title()
                    sc_street_type = row[4]
                    sc_locality_name = row[5].title()
                    sc_state_territory = row[6]
                    sc_postcode = row[7]
                    sc_latitude = row[8]
                    sc_longitude = row[9]
                    sc_geocode_type = row[10].title()
                    sc_confidence = row[11]
                    sc_date_created = row[12]
                    sc_date_last_modified = row[13]
                    sc_date_retired = row[14]
                    sc_building_name = row[15]
                    sc_lot_number_prefix = row[16]
                    sc_lot_number = row[17]
                    sc_lot_number_suffix = row[18]
                    sc_flat_type_code = row[19]
                    sc_flat_number_prefix = row[20]
                    sc_flat_number = row[21]
                    sc_flat_number_suffix = row[22]
                    sc_level_type_code = row[23]
                    sc_level_number_prefix = row[24]
                    sc_level_number = row[25]
                    sc_level_number_suffix = row[26]
                    sc_number_first_prefix = row[27]
                    sc_number_first_suffix = row[28]
                    sc_number_last_prefix = row[29]
                    sc_number_last = row[30]
                    sc_number_last_suffix = row[31]

                    secondary_address_string, secondary_street_string = self.format_address(
                        level_type_code=sc_level_type_code, level_number_prefix=sc_level_number_prefix,
                        level_number=sc_level_number, level_number_suffix=sc_level_number_suffix,
                        flat_type_code=sc_flat_type_code, flat_number_prefix=sc_flat_number_prefix, flat_number=sc_flat_number,
                        flat_number_suffix=sc_flat_number_suffix,
                        number_first_prefix=sc_number_first_prefix, number_first=sc_street_number_1,
                        number_first_suffix=sc_number_first_suffix,
                        number_last_prefix=sc_number_last_prefix, number_last=sc_number_last,
                        number_last_suffix=sc_number_last_suffix,
                        building=sc_building_name, lot_number_prefix=sc_lot_number_prefix, lot_number=sc_lot_number,
                        lot_number_suffix=sc_lot_number_suffix,
                        street_name=sc_street_name, street_type=sc_street_type,
                        locality=sc_locality_name, state_territory=sc_state_territory, postcode=sc_postcode
                    )
                    self.secondary_addresses[row[32]] = secondary_address_string
            except Exception as e:
                print("DB conn 4, can't connect to DB for query s4. Invalid dbname, user or password?")
                print(e)

            # get a list of primaryIds from the primary_secondary table
            s5 = sql.SQL('''SELECT 
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
                        c.primary_pid,
                        c.ps_join_type_code                                        
                    FROM 
                        {dbschema}.primary_secondary c
                          INNER JOIN {dbschema}.address_view a ON c.primary_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
                    WHERE secondary_pid = {id}''') \
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
                cursor.execute(s5)
                rows = cursor.fetchall()
                for row in rows:
                    pr_street_locality_pid = row[0]
                    pr_locality_pid = row[1]
                    pr_street_number_1 = row[2]
                    pr_street_name = row[3].title()
                    pr_street_type = row[4]
                    pr_locality_name = row[5].title()
                    pr_state_territory = row[6]
                    pr_postcode = row[7]
                    pr_latitude = row[8]
                    pr_longitude = row[9]
                    pr_geocode_type = row[10].title()
                    pr_confidence = row[11]
                    pr_date_created = row[12]
                    pr_date_last_modified = row[13]
                    pr_date_retired = row[14]
                    pr_building_name = row[15]
                    pr_lot_number_prefix = row[16]
                    pr_lot_number = row[17]
                    pr_lot_number_suffix = row[18]
                    pr_flat_type_code = row[19]
                    pr_flat_number_prefix = row[20]
                    pr_flat_number = row[21]
                    pr_flat_number_suffix = row[22]
                    pr_level_type_code = row[23]
                    pr_level_number_prefix = row[24]
                    pr_level_number = row[25]
                    pr_level_number_suffix = row[26]
                    pr_number_first_prefix = row[27]
                    pr_number_first_suffix = row[28]
                    pr_number_last_prefix = row[29]
                    pr_number_last = row[30]
                    pr_number_last_suffix = row[31]

                    primary_address_string, primary_street_string = self.format_address(
                        level_type_code=pr_level_type_code, level_number_prefix=pr_level_number_prefix,
                        level_number=pr_level_number, level_number_suffix=pr_level_number_suffix,
                        flat_type_code=pr_flat_type_code, flat_number_prefix=pr_flat_number_prefix, flat_number=pr_flat_number,
                        flat_number_suffix=pr_flat_number_suffix,
                        number_first_prefix=pr_number_first_prefix, number_first=pr_street_number_1,
                        number_first_suffix=pr_number_first_suffix,
                        number_last_prefix=pr_number_last_prefix, number_last=pr_number_last,
                        number_last_suffix=pr_number_last_suffix,
                        building=pr_building_name, lot_number_prefix=pr_lot_number_prefix, lot_number=pr_lot_number,
                        lot_number_suffix=pr_lot_number_suffix,
                        street_name=pr_street_name, street_type=pr_street_type,
                        locality=pr_locality_name, state_territory=pr_state_territory, postcode=pr_postcode
                    )
                    self.primary_addresses[row[32]] = primary_address_string
            except Exception as e:
                print("DB conn 5, can't connect to DB for query s5. Invalid dbname, user or password?")
                print(e)

            # get a list of mb2011s from the address_mesh_block_2011 and mb_2011 tables
            s6 = sql.SQL('''SELECT 
                        mb_2011_code,
                        mb_match_code                
                    FROM {dbschema}.address_mesh_block_2011_view
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
                cursor.execute(s6)
                rows = cursor.fetchall()
                for row in rows:
                    self.mesh_block_2011s.append(row[0])
            except Exception as e:
                print("DB conn 6, can't connect to DB for query s6. Invalid dbname, user or password?")
                print(e)

            # get a list of mb2016s from the address_mesh_block_2016 and mb_2016 tables
            s7 = sql.SQL('''SELECT 
                        mb_2016_code,
                        mb_match_code                
                    FROM {dbschema}.address_mesh_block_2016_view
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
                cursor.execute(s7)
                rows = cursor.fetchall()
                for row in rows:
                    self.mesh_block_2016s.append(row[0])
            except Exception as e:
                print("DB conn 7, can't connect to DB for query s7. Invalid dbname, user or password?")
                print(e)

            print('address_site_pid: ' + str(address_site_pid))
            view_html = render_template(
                'class_address_gnaf.html',
                address_string=this_address_string,
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
                alias_addresses=self.alias_addresses,
                principal_addresses=self.principal_addresses,
                secondary_addresses=self.secondary_addresses,
                primary_addresses=self.primary_addresses,
                mesh_block_2011_uri=config.URI_MB_2011_INSTANCE_BASE + '%s',
                mesh_block_2011s=self.mesh_block_2011s,
                mesh_block_2016_uri=config.URI_MB_2016_INSTANCE_BASE + '%s',
                mesh_block_2016s=self.mesh_block_2016s,
                street_string=this_street_string
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
                    geometry_wkt = 'SRID=GDA94;POINT({} {})'.format(record[8], record[9])
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

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))
