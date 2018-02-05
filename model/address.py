from _config import reg
from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
import psycopg2
from psycopg2 import sql
import model.gnaf_ont_lookups as LOOKUPS


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
        self.address_positions = dict()
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
            flat_num = '{}{}{}'.format(
                flat_number_prefix if flat_number_prefix is not None else '',
                flat_number if flat_number is not None else '',
                flat_number_suffix if flat_number_suffix is not None else '')
            level_num = '{}{}{}'.format(
                level_number_prefix if level_number_prefix is not None else '',
                level_number if level_number is not None else '',
                level_number_suffix if level_number_suffix is not None else '')
            lot_num = '{}{}{}'.format(
                lot_number_prefix if lot_number_prefix is not None else '',
                lot_number if lot_number is not None else '',
                lot_number_suffix if lot_number_suffix is not None else '')
            num_first = '{}{}{}'.format(
                number_first_prefix if number_first_prefix is not None else '',
                number_first if number_first is not None else '',
                number_first_suffix if number_first_suffix is not None else '')
            num_last = '{}{}{}'.format(
                number_last_prefix if number_last_prefix is not None else '',
                number_last if number_last is not None else '',
                number_last_suffix if number_last_suffix is not None else '')
            if level_type_code is not None:
                address_string += level_type_code.title() + ' '
            if level_num is not '':
                address_string += level_num + ' '
            if flat_num is not '':
                if flat_type_code is not None:
                    address_string += '{flattype} {flatnum} '.format(
                        flattype=flat_type_code.title(),
                        flatnum=flat_num
                    )
                else:
                    address_string += flat_num + ' '
            if building is not None:
                address_string += building.title() + ' '
            if num_first is not '':
                address_string += num_first
                if num_last is not '':
                    address_string += '-' + num_last
                address_string += ' '
            else:
                address_string += 'LOT {lotnum} '.format(lotnum=lot_num)

            address_string += '{st}, {loc}, {state} {postcode}'.format(
                st=street_string,
                loc=locality,
                state=state_territory,
                postcode=postcode
            )

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
            number_first = None
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

            # DB connection
            cursor = config.get_db_cursor()

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
                        g.geocode_type_code,
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
                    FROM {dbschema}.address_view a 
                    INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
                    INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                    WHERE a.address_detail_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s)
            rows = cursor.fetchall()
            for row in rows:
                r = config.reg(cursor, row)
                street_locality_pid = row[0]
                locality_pid = row[1]
                street_name = row[3].title()
                street_type = row[4]
                locality_name = row[5].title()
                state_territory = row[6]
                postcode = row[7]
                latitude = row[8]
                longitude = row[9]
                geocode_type = row[10].title()
                print(r.geocode_type_code)
                geocode_type_uri = LOOKUPS.geocode_subclass.get(r.geocode_type_code)
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
                number_first = row[2]
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
                geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(latitude, longitude)

            this_address_string, this_street_string = self.format_address(
                level_type_code=level_type_code, level_number_prefix=level_number_prefix,
                level_number=level_number, level_number_suffix=level_number_suffix,
                flat_type_code=flat_type_code, flat_number_prefix=flat_number_prefix,
                flat_number=flat_number, flat_number_suffix=flat_number_suffix,
                number_first_prefix=number_first_prefix, number_first=number_first,
                number_first_suffix=number_first_suffix, number_last_prefix=number_last_prefix,
                number_last=number_last, number_last_suffix=number_last_suffix,
                building=building_name, lot_number_prefix=lot_number_prefix,
                lot_number=lot_number, lot_number_suffix=lot_number_suffix,
                street_name=street_name, street_type=street_type,
                locality=locality_name, state_territory=state_territory, postcode=postcode
            )

            # get a list of aliasIds from the address_alias table
            s2 = sql.SQL('''SELECT 
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.alias_pid,
                        c.alias_type_code                                        
                    FROM {dbschema}.address_alias c
                    INNER JOIN {dbschema}.address_detail a ON c.alias_pid = a.address_detail_pid
                    INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                    INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                    INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                    INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                    INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
                    WHERE principal_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s2)
            rows = cursor.fetchall()
            for row in rows:
                    al_street_locality_pid = row[0]
                    al_locality_pid = row[1]
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
                    al_number_first = row[2]
                    al_number_first_suffix = row[28]
                    al_number_last_prefix = row[29]
                    al_number_last = row[30]
                    al_number_last_suffix = row[31]

                    alias_address_string, alias_street_string = self.format_address(
                        level_type_code=al_level_type_code, level_number_prefix=al_level_number_prefix,
                        level_number=al_level_number, level_number_suffix=al_level_number_suffix,
                        flat_type_code=al_flat_type_code, flat_number_prefix=al_flat_number_prefix, flat_number=al_flat_number,
                        flat_number_suffix=al_flat_number_suffix,
                        number_first_prefix=al_number_first_prefix, number_first=al_number_first,
                        number_first_suffix=al_number_first_suffix,
                        number_last_prefix=al_number_last_prefix, number_last=al_number_last,
                        number_last_suffix=al_number_last_suffix,
                        building=al_building_name, lot_number_prefix=al_lot_number_prefix, lot_number=al_lot_number,
                        lot_number_suffix=al_lot_number_suffix,
                        street_name=al_street_name, street_type=al_street_type,
                        locality=al_locality_name, state_territory=al_state_territory, postcode=al_postcode
                    )
                    self.alias_addresses[row[32]] = alias_address_string

            # get a list of principalIds from the address_alias table
            s3 = sql.SQL('''SELECT 
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.principal_pid,
                        c.alias_type_code                                        
                    FROM {dbschema}.address_alias c
                    INNER JOIN {dbschema}.address_detail a ON c.principal_pid = a.address_detail_pid
                    INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                    INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                    INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                    INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                    INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
                    WHERE alias_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s3)
            rows = cursor.fetchall()
            for row in rows:
                    pc_street_locality_pid = row[0]
                    pc_locality_pid = row[1]
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
                    pc_number_first = row[2]
                    pc_number_first_suffix = row[28]
                    pc_number_last_prefix = row[29]
                    pc_number_last = row[30]
                    pc_number_last_suffix = row[31]

                    principal_address_string, principal_street_string = self.format_address(
                        level_type_code=pc_level_type_code, level_number_prefix=pc_level_number_prefix,
                        level_number=pc_level_number, level_number_suffix=pc_level_number_suffix,
                        flat_type_code=pc_flat_type_code, flat_number_prefix=pc_flat_number_prefix, flat_number=pc_flat_number,
                        flat_number_suffix=pc_flat_number_suffix,
                        number_first_prefix=pc_number_first_prefix, number_first=pc_number_first,
                        number_first_suffix=pc_number_first_suffix,
                        number_last_prefix=pc_number_last_prefix, number_last=pc_number_last,
                        number_last_suffix=pc_number_last_suffix,
                        building=pc_building_name, lot_number_prefix=pc_lot_number_prefix, lot_number=pc_lot_number,
                        lot_number_suffix=pc_lot_number_suffix,
                        street_name=pc_street_name, street_type=pc_street_type,
                        locality=pc_locality_name, state_territory=pc_state_territory, postcode=pc_postcode
                    )
                    self.principal_addresses[row[32]] = principal_address_string

            # get a list of secondaryIds from the primary_secondary table
            s4 = sql.SQL('''SELECT 
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.secondary_pid,
                        c.ps_join_type_code                                        
                    FROM {dbschema}.primary_secondary c
                    INNER JOIN {dbschema}.address_detail a ON c.secondary_pid = a.address_detail_pid
                    INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                    INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                    INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                    INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                    INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
                    WHERE primary_pid = {id}''') \
                .format(dbschema=sql.Identifier(config.DB_SCHEMA), id=sql.Literal(self.id))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s4)
            rows = cursor.fetchall()
            for row in rows:
                    sc_street_locality_pid = row[0]
                    sc_locality_pid = row[1]
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
                    sc_number_first = row[2]
                    sc_number_first_suffix = row[28]
                    sc_number_last_prefix = row[29]
                    sc_number_last = row[30]
                    sc_number_last_suffix = row[31]

                    secondary_address_string, secondary_street_string = self.format_address(
                        level_type_code=sc_level_type_code, level_number_prefix=sc_level_number_prefix,
                        level_number=sc_level_number, level_number_suffix=sc_level_number_suffix,
                        flat_type_code=sc_flat_type_code, flat_number_prefix=sc_flat_number_prefix, flat_number=sc_flat_number,
                        flat_number_suffix=sc_flat_number_suffix,
                        number_first_prefix=sc_number_first_prefix, number_first=number_first,
                        number_first_suffix=sc_number_first_suffix,
                        number_last_prefix=sc_number_last_prefix, number_last=sc_number_last,
                        number_last_suffix=sc_number_last_suffix,
                        building=sc_building_name, lot_number_prefix=sc_lot_number_prefix, lot_number=sc_lot_number,
                        lot_number_suffix=sc_lot_number_suffix,
                        street_name=sc_street_name, street_type=sc_street_type,
                        locality=sc_locality_name, state_territory=sc_state_territory, postcode=sc_postcode
                    )
                    self.secondary_addresses[row[32]] = secondary_address_string

            # get a list of primaryIds from the primary_secondary table
            s5 = sql.SQL('''SELECT 
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.primary_pid,
                        c.ps_join_type_code                                        
                    FROM {dbschema}.primary_secondary c
                    INNER JOIN {dbschema}.address_detail a ON c.primary_pid = a.address_detail_pid
                    INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                    INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                    INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                    INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                    INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
                    WHERE secondary_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s5)
            rows = cursor.fetchall()
            for row in rows:
                pr_street_locality_pid = row[0]
                pr_locality_pid = row[1]
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
                pr_number_first = row[2]
                pr_number_first_suffix = row[28]
                pr_number_last_prefix = row[29]
                pr_number_last = row[30]
                pr_number_last_suffix = row[31]

                primary_address_string, primary_street_string = self.format_address(
                    level_type_code=pr_level_type_code, level_number_prefix=pr_level_number_prefix,
                    level_number=pr_level_number, level_number_suffix=pr_level_number_suffix,
                    flat_type_code=pr_flat_type_code, flat_number_prefix=pr_flat_number_prefix, flat_number=pr_flat_number,
                    flat_number_suffix=pr_flat_number_suffix,
                    number_first_prefix=pr_number_first_prefix, number_first=pr_number_first,
                    number_first_suffix=pr_number_first_suffix,
                    number_last_prefix=pr_number_last_prefix, number_last=pr_number_last,
                    number_last_suffix=pr_number_last_suffix,
                    building=pr_building_name, lot_number_prefix=pr_lot_number_prefix, lot_number=pr_lot_number,
                    lot_number_suffix=pr_lot_number_suffix,
                    street_name=pr_street_name, street_type=pr_street_type,
                    locality=pr_locality_name, state_territory=pr_state_territory, postcode=pr_postcode
                )
                self.primary_addresses[row[32]] = primary_address_string

            # get a list of mb2011s from the address_mesh_block_2011 and mb_2011 tables
            s6 = sql.SQL('''SELECT 
                        mb_2011_code,
                        mb_match_code                
                    FROM {dbschema}.address_mesh_block_2011_view
                    WHERE address_detail_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s6)
            rows = cursor.fetchall()
            for row in rows:
                self.mesh_block_2011s.append(row[0])

            # get a list of mb2016s from the address_mesh_block_2016 and mb_2016 tables
            s7 = sql.SQL('''SELECT 
                        mb_2016_code,
                        mb_match_code                
                    FROM {dbschema}.address_mesh_block_2016_view
                    WHERE address_detail_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s7)
            rows = cursor.fetchall()
            for row in rows:
                self.mesh_block_2016s.append(row[0])

            view_html = render_template(
                'class_address_gnaf.html',
                address_string=this_address_string,
                address_detail_pid=self.id,
                street_name=street_name,
                street_type=street_type,
                locality_name=locality_name,
                state_territory=state_territory,
                postcode=postcode,
                latitude=latitude,
                longitude=longitude,
                geocode_type=geocode_type,
                geocode_type_uri=geocode_type_uri,
                confidence=confidence,
                geometry_wkt=geometry_wkt,
                date_created=date_created,
                date_last_modified=date_last_modified,
                date_retired=date_retired,
                building_name=building_name,
                number_lot_prefix=lot_number_prefix,
                number_lot=lot_number,
                number_lot_suffix=lot_number_suffix,
                flat_type_code=flat_type_code,
                number_flat_prefix=flat_number_prefix,
                number_flat=flat_number,
                number_flat_suffix=flat_number_suffix,
                level_type_code=level_type_code,
                number_level_prefix=level_number_prefix,
                number_level=level_number,
                number_level_suffix=level_number_suffix,
                number_first=number_first,
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
            # initialise all varables in case not found by SQL
            street_locality_pid = None
            locality_pid = None
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
                    number_first = row[2]
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
                    geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(latitude, longitude)
            except Exception as e:
                print("DB conn 1 can't connect to DB for query s. Invalid dbname, user or password?")
                print(e)

            this_address_string, this_street_string = self.format_address(
                level_type_code=level_type_code, level_number_prefix=level_number_prefix, level_number=level_number, level_number_suffix=level_number_suffix,
                flat_type_code=flat_type_code, flat_number_prefix=flat_number_prefix, flat_number=flat_number, flat_number_suffix=flat_number_suffix,
                number_first_prefix=number_first_prefix, number_first=number_first, number_first_suffix=number_first_suffix,
                number_last_prefix=number_last_prefix, number_last=number_last, number_last_suffix=number_last_suffix,
                building=building_name, lot_number_prefix=lot_number_prefix, lot_number=lot_number, lot_number_suffix=lot_number_suffix,
                street_name=street_name, street_type=street_type,
                locality=locality_name, state_territory=state_territory, postcode=postcode
            )

            # get a list of aliasIds from the address_alias table
            s2 = sql.SQL('''SELECT 
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.alias_pid,
                        c.alias_type_code                                        
                    FROM 
                        {dbschema}.address_alias c
                          INNER JOIN {dbschema}.address_detail a ON c.alias_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                          INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                          INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                          INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                          INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
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
                    al_number_first = row[2]
                    al_number_first_suffix = row[28]
                    al_number_last_prefix = row[29]
                    al_number_last = row[30]
                    al_number_last_suffix = row[31]

                    alias_address_string, alias_street_string = self.format_address(
                        level_type_code=al_level_type_code, level_number_prefix=al_level_number_prefix,
                        level_number=al_level_number, level_number_suffix=al_level_number_suffix,
                        flat_type_code=al_flat_type_code, flat_number_prefix=al_flat_number_prefix, flat_number=al_flat_number,
                        flat_number_suffix=al_flat_number_suffix,
                        number_first_prefix=al_number_first_prefix, number_first=al_number_first,
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
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.principal_pid,
                        c.alias_type_code                                        
                    FROM 
                        {dbschema}.address_alias c
                          INNER JOIN {dbschema}.address_detail a ON c.principal_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                          INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                          INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                          INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                          INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
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
                    pc_number_first = row[2]
                    pc_number_first_suffix = row[28]
                    pc_number_last_prefix = row[29]
                    pc_number_last = row[30]
                    pc_number_last_suffix = row[31]

                    principal_address_string, principal_street_string = self.format_address(
                        level_type_code=pc_level_type_code, level_number_prefix=pc_level_number_prefix,
                        level_number=pc_level_number, level_number_suffix=pc_level_number_suffix,
                        flat_type_code=pc_flat_type_code, flat_number_prefix=pc_flat_number_prefix, flat_number=pc_flat_number,
                        flat_number_suffix=pc_flat_number_suffix,
                        number_first_prefix=pc_number_first_prefix, number_first=pc_number_first,
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
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.secondary_pid,
                        c.ps_join_type_code                                        
                    FROM 
                        {dbschema}.primary_secondary c
                          INNER JOIN {dbschema}.address_detail a ON c.secondary_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                          INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                          INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                          INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                          INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
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
                    sc_number_first = row[2]
                    sc_number_first_suffix = row[28]
                    sc_number_last_prefix = row[29]
                    sc_number_last = row[30]
                    sc_number_last_suffix = row[31]

                    secondary_address_string, secondary_street_string = self.format_address(
                        level_type_code=sc_level_type_code, level_number_prefix=sc_level_number_prefix,
                        level_number=sc_level_number, level_number_suffix=sc_level_number_suffix,
                        flat_type_code=sc_flat_type_code, flat_number_prefix=sc_flat_number_prefix, flat_number=sc_flat_number,
                        flat_number_suffix=sc_flat_number_suffix,
                        number_first_prefix=sc_number_first_prefix, number_first=sc_number_first,
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
                        a.street_locality_pid, 
                        a.locality_pid, 
                        CAST(a.number_first AS text), 
                        s.street_name, 
                        s.street_type_code, 
                        l.locality_name, 
                        st.state_abbreviation, 
                        a.postcode ,
                        g.latitude,
                        g.longitude,
                        gt.name AS geocode_type,
                        CAST(a.confidence AS text),
                        CAST(a.date_created AS text),
                        CAST(a.date_last_modified AS text),
                        CAST(a.date_retired AS text),
                        a.building_name,
                        a.lot_number_prefix,
                        a.lot_number,
                        a.lot_number_suffix,
                        a.flat_type_code,
                        a.flat_number_prefix,
                        CAST(a.flat_number AS text),
                        a.flat_number_suffix,
                        a.level_type_code,
                        a.level_number_prefix,
                        CAST(a.level_number AS text),
                        a.level_number_suffix,
                        a.number_first_prefix,
                        a.number_first_suffix,
                        a.number_last_prefix,
                        CAST(a.number_last AS text),
                        a.number_last_suffix,
                        c.primary_pid,
                        c.ps_join_type_code                                        
                    FROM 
                        {dbschema}.primary_secondary c
                          INNER JOIN {dbschema}.address_detail a ON c.primary_pid = a.address_detail_pid
                          INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid
                          INNER JOIN {dbschema}.geocode_type_aut gt ON g.geocode_type_code = gt.code
                          INNER JOIN {dbschema}.street_locality s ON a.street_locality_pid = s.street_locality_pid
                          INNER JOIN {dbschema}.locality l ON s.locality_pid = l.locality_pid
                          INNER JOIN {dbschema}.state st ON l.state_pid = st.state_pid
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
                    pr_number_first = row[2]
                    pr_number_first_suffix = row[28]
                    pr_number_last_prefix = row[29]
                    pr_number_last = row[30]
                    pr_number_last_suffix = row[31]

                    primary_address_string, primary_street_string = self.format_address(
                        level_type_code=pr_level_type_code, level_number_prefix=pr_level_number_prefix,
                        level_number=pr_level_number, level_number_suffix=pr_level_number_suffix,
                        flat_type_code=pr_flat_type_code, flat_number_prefix=pr_flat_number_prefix, flat_number=pr_flat_number,
                        flat_number_suffix=pr_flat_number_suffix,
                        number_first_prefix=pr_number_first_prefix, number_first=pr_number_first,
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

            # get a list of address site geocodes from the address_site_geocode tables
            s8 = sql.SQL('''SELECT 
                        b.address_site_geocode_pid,
                        c.name AS geocode_type                
                    FROM {dbschema}.address_detail a
                          INNER JOIN {dbschema}.address_site_geocode b ON a.address_site_pid = b.address_site_pid
                          INNER JOIN {dbschema}.geocode_type_aut c ON b.geocode_type_code = c.code
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
                cursor.execute(s8)
                rows = cursor.fetchall()
                for row in rows:
                    self.address_positions[row[0]] = row[1]
            except Exception as e:
                print("DB conn 7, can't connect to DB for query s7. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_address_ISO19160.html',
                address_string=this_address_string,
                address_detail_pid=self.id,
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
                number_first=number_first,
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
                street_string=this_street_string,
                address_positions=self.address_positions
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
                    geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(record[8], record[9])
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
                        flat_type,
                        flat_number,
                        level_type,
                        level_number,
                        CAST(number_first AS text), 
                        CAST(number_last AS text), 
                        street_name, 
                        street_type_code, 
                        street_suffix_code,
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
                    ac_flat_type_value = record[2].title() if record[2] is not None else None
                    ac_flat_number_value = record[3]
                    ac_level_type_value = record[4].title() if record[4] is not None else None
                    ac_level_number_value = record[5]
                    ac_street_number_low_value = record[6]
                    ac_street_number_high_value = record[7]
                    ac_street_name_value = record[8].title()
                    ac_street_type_value = record[9].title() if record[9] is not None else None
                    ac_street_suffix_value = record[10].title() if record[10] is not None else None
                    ac_locality_value = record[11].title()
                    ac_state_value = record[12]
                    ac_postcode_value = record[13]
                    geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(record[14], record[15])
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            AddressComponentTypeUriBase = 'http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressComponentType/'
            AddressPositionTypeUriBase = 'http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressPositionType/'

            ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
            g.bind('iso19160', ISO)

            GEO = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geo', GEO)

            g.add((a, RDF.type, ISO.Address))

            if ac_flat_type_value is not None or ac_flat_number_value is not None:
                ac_unit = BNode()
                g.add((ac_unit, RDF.type, ISO.AddressComponent))
                g.add((ac_unit, ISO.type, URIRef(AddressComponentTypeUriBase + 'unit')))
                g.add((a, ISO.addressComponent, ac_unit))

            if ac_flat_type_value is not None:
                ac_unit_type = BNode()
                g.add((ac_unit_type, RDF.type, ISO.AddressComponent))
                g.add((ac_unit_type, ISO.valueInformation, Literal(ac_flat_type_value, datatype=XSD.string)))
                g.add((ac_unit_type, ISO.type, URIRef(AddressComponentTypeUriBase + 'unitType')))
                g.add((ac_unit, ISO.valueComponent, ac_unit_type))

            if ac_flat_number_value is not None:
                ac_unit_value = BNode()
                g.add((ac_unit_value, RDF.type, ISO.AddressComponent))
                g.add((ac_unit_value, ISO.valueInformation, Literal(ac_flat_number_value, datatype=XSD.string)))
                g.add((ac_unit_value, ISO.type, URIRef(AddressComponentTypeUriBase + 'unitValue')))
                g.add((ac_unit, ISO.valueComponent, ac_unit_value))

            if ac_level_type_value is not None or ac_level_number_value is not None:
                ac_level = BNode()
                g.add((ac_level, RDF.type, ISO.AddressComponent))
                g.add((ac_level, ISO.type, URIRef(AddressComponentTypeUriBase + 'level')))
                g.add((a, ISO.addressComponent, ac_level))

            if (ac_level_type_value is not None):
                ac_level_type = BNode()
                g.add((ac_level_type, RDF.type, ISO.AddressComponent))
                g.add((ac_level_type, ISO.valueInformation, Literal(ac_level_type_value, datatype=XSD.string)))
                g.add((ac_level_type, ISO.type, URIRef(AddressComponentTypeUriBase + 'levelType')))
                g.add((ac_level, ISO.valueComponent, ac_level_type))

            if (ac_level_number_value is not None):
                ac_level_value = BNode()
                g.add((ac_level_value, RDF.type, ISO.AddressComponent))
                g.add((ac_level_value, ISO.valueInformation, Literal(ac_level_number_value, datatype=XSD.string)))
                g.add((ac_level_value, ISO.type, URIRef(AddressComponentTypeUriBase + 'levelValue')))
                g.add((ac_level, ISO.valueComponent, ac_level_value))

            ac_address_number = BNode()
            g.add((ac_address_number, RDF.type, ISO.AddressComponent))
            g.add((ac_address_number, ISO.type, URIRef(AddressComponentTypeUriBase + 'addressNumber')))
            g.add((a, ISO.addressComponent, ac_address_number))

            if ac_street_number_low_value is not None:
                ac_address_number_low = BNode()
                g.add((ac_address_number_low, RDF.type, ISO.AddressComponent))
                g.add((ac_address_number_low, ISO.valueInformation, Literal(ac_street_number_low_value, datatype=XSD.string)))
                g.add((ac_address_number_low, ISO.type, URIRef(AddressComponentTypeUriBase + 'addressNumberLow')))
                g.add((ac_address_number, ISO.valueComponent, ac_address_number_low))

            if ac_street_number_high_value is not None:
                ac_address_number_high = BNode()
                g.add((ac_address_number_high, RDF.type, ISO.AddressComponent))
                g.add((ac_address_number_high, ISO.valueInformation, Literal(ac_street_number_high_value, datatype=XSD.string)))
                g.add((ac_address_number_high, ISO.type, URIRef(AddressComponentTypeUriBase + 'addressNumberHigh')))
                g.add((ac_address_number, ISO.valueComponent, ac_address_number_high))

            ac_street = BNode()
            g.add((ac_street, RDF.type, ISO.AddressComponent))
            g.add((ac_street, ISO.type, URIRef(AddressComponentTypeUriBase + 'thoroughfare')))
            g.add((a, ISO.addressComponent, ac_street))

            ac_street_name = BNode()
            g.add((ac_street_name, RDF.type, ISO.AddressComponent))
            g.add((ac_street_name, ISO.valueInformation, Literal(ac_street_name_value, datatype=XSD.string)))
            g.add((ac_street_name, ISO.type, URIRef(AddressComponentTypeUriBase + 'thoroughfareName')))
            g.add((ac_street, ISO.valueComponent, ac_street_name))

            if ac_street_type_value is not None:
                ac_street_type = BNode()
                g.add((ac_street_type, RDF.type, ISO.AddressComponent))
                g.add((ac_street_type, ISO.valueInformation, Literal(ac_street_type_value, datatype=XSD.string)))
                g.add((ac_street_type, ISO.type, URIRef(AddressComponentTypeUriBase + 'thoroughfareType')))
                g.add((ac_street, ISO.valueComponent, ac_street_type))

            if ac_street_suffix_value is not None:
                ac_street_suffix = BNode()
                g.add((ac_street_suffix, RDF.type, ISO.AddressComponent))
                g.add((ac_street_suffix, ISO.valueInformation, Literal(ac_street_suffix_value, datatype=XSD.string)))
                g.add((ac_street_suffix, ISO.type, URIRef(AddressComponentTypeUriBase + 'thoroughfareSuffix')))
                g.add((ac_street, ISO.valueComponent, ac_street_suffix))

            ac_locality = BNode()
            g.add((ac_locality, RDF.type, ISO.AddressComponent))
            g.add((ac_locality, ISO.valueInformation, Literal(ac_locality_value, datatype=XSD.string)))
            g.add((ac_locality, ISO.type, URIRef(AddressComponentTypeUriBase + 'locality')))
            g.add((a, ISO.addressComponent, ac_locality))

            ac_state = BNode()
            g.add((ac_state, RDF.type, ISO.AddressComponent))
            g.add((ac_state, ISO.valueInformation, Literal(ac_state_value, datatype=XSD.string)))
            g.add((ac_state, ISO.type, URIRef(AddressComponentTypeUriBase + 'stateTerritory')))
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
            GNAF = Namespace('http://gnafld.org/def/gnaf/')
            g.bind('gnaf', GNAF)

            GEO = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geo', GEO)

            PROV = Namespace('http://www.w3.org/ns/prov#')
            g.bind('prov', PROV)

            DCT = Namespace('http://purl.org/dc/terms/')
            g.bind('dct', DCT)

            # RDF: declare Address instance
            g.add((a, RDF.type, GNAF.Address))

            # get the details from DB
            s = sql.SQL('''SELECT * 
                           FROM {dbschema}.address_detail d
                           INNER JOIN gnaf.address_default_geocode g
                           ON d.address_detail_pid = g.address_detail_pid
                           WHERE d.address_detail_pid = {id}''') \
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
            except Exception as e:
                print("DB can't connect to DB for query {}. Invalid dbname, user or password?".format(s))
                print(e)

            cursor = conn.cursor()
            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s)
            rows = cursor.fetchall()
            for row in rows:
                r = config.reg(cursor, row)

                # RDF: geometry
                geometry_wkt = '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'\
                    .format(r.longitude, r.latitude)
                geocode = BNode()
                g.add((geocode, RDF.type, URIRef(LOOKUPS.geocode_subclass.get(r.geocode_type_code))))
                g.add((geocode, GEO.asWKT, Literal(geometry_wkt, datatype=GEO.wktLiteral)))
                g.add((a, GEO.hasGeometry, geocode))

                if r.private_street is not None:
                    g.add((a, GNAF.hasPrivateStreet, Literal(True, datatype=XSD.boolean)))
                else:
                    g.add((a, GNAF.hasPrivateStreet, Literal(False, datatype=XSD.boolean)))

                g.add((a, GNAF.hasStreet, URIRef(config.URI_STREET_INSTANCE_BASE + str(r.street_locality_pid))))

                g.add((a, GNAF.hasGnafConfidence, URIRef(LOOKUPS.confidence.get(r.confidence))))

                if r.address_site_pid is not None:
                    g.add((a, GNAF.hasAddressSite, URIRef('http://gnafld.net/addressSite/' + str(r.address_site_pid))))

                # RDF: Numbers
                # lot_number
                if r.lot_number is not None:
                    lot_number = BNode()
                    g.add((lot_number, RDF.type, GNAF.LotNumber))
                    g.add((lot_number, PROV.value, Literal(int(r.lot_number), datatype=XSD.integer)))
                    g.add((a, GNAF.hasNumber, lot_number))
                    if r.lot_number_prefix is not None:
                        g.add((lot_number, GNAF.hasPrefix, Literal(str(r.lot_number_prefix), datatype=XSD.string)))
                    if r.lot_number_suffix is not None:
                        g.add((lot_number, GNAF.hasSuffix, Literal(str(r.lot_number_suffix), datatype=XSD.string)))

                # TODO: represent flat_type_code

                # flat_number
                if r.flat_number is not None:
                    flat_number = BNode()
                    g.add((flat_number, RDF.type, GNAF.FlatNumber))
                    g.add((flat_number, PROV.value, Literal(int(r.flat_number), datatype=XSD.integer)))
                    g.add((a, GNAF.hasNumber, flat_number))
                    if r.flat_number_prefix is not None:
                        g.add((flat_number, GNAF.hasPrefix, Literal(str(r.flat_number_prefix), datatype=XSD.string)))
                    if r.flat_number_suffix is not None:
                        g.add((flat_number, GNAF.hasSuffix, Literal(str(r.flat_number_suffix), datatype=XSD.string)))
                # level_number
                if r.level_number is not None:
                    level_number = BNode()
                    g.add((level_number, RDF.type, GNAF.LevelNumber))
                    g.add((level_number, PROV.value, Literal(int(r.level_number), datatype=XSD.integer)))
                    g.add((a, GNAF.hasNumber, level_number))
                    if r.level_number_prefix is not None:
                        g.add((level_number, GNAF.hasPrefix, Literal(str(r.level_number_prefix), datatype=XSD.string)))
                    if r.level_number_suffix is not None:
                        g.add((level_number, GNAF.hasSuffix, Literal(str(r.level_number_suffix), datatype=XSD.string)))
                # number_first
                if r.number_first is not None:
                    number_first = BNode()
                    g.add((number_first, RDF.type, GNAF.FirstStreetNumber))
                    g.add((number_first, PROV.value, Literal(int(r.number_first), datatype=XSD.integer)))
                    g.add((a, GNAF.hasNumber, number_first))
                    if r.number_first_prefix is not None:
                        g.add((number_first, GNAF.hasPrefix, Literal(str(r.number_first_prefix), datatype=XSD.string)))
                    if r.number_first_suffix is not None:
                        g.add((number_first, GNAF.hasSuffix, Literal(str(r.number_first_suffix), datatype=XSD.string)))
                # number_last
                if r.number_last is not None:
                    number_last = BNode()
                    g.add((number_last, RDF.type, GNAF.LastStreetNumber))
                    g.add((number_last, PROV.value, Literal(int(r.number_last), datatype=XSD.integer)))
                    g.add((a, GNAF.hasNumber, number_last))
                    if r.number_last_prefix is not None:
                        g.add((number_last, GNAF.hasPrefix, Literal(str(r.number_last_prefix), datatype=XSD.string)))
                    if r.number_last_suffix is not None:
                        g.add((number_last, GNAF.hasSuffix, Literal(str(r.number_last_suffix), datatype=XSD.string)))

                # RDF: locality
                g.add((a, GNAF.hasLocality, URIRef(config.URI_LOCALITY_INSTANCE_BASE + row[24])))

                # RDF: data properties
                if r.location_description is not None:
                    g.add((a, DCT.description, Literal(r.location_description, datatype=XSD.string)))

                g.add((a, GNAF.hasPostcode, Literal(r.postcode, datatype=XSD.integer)))

                if r.building_name is not None:
                    g.add((a, GNAF.hasBuldingName, Literal(r.building_name, datatype=XSD.string)))

                g.add((a, GNAF.hasDateCreated, Literal(r.date_created, datatype=XSD.date)))
                g.add((a, GNAF.hasDateLastModified, Literal(r.date_last_modified, datatype=XSD.date)))
                if r.date_retired is not None:
                    g.add((a, GNAF.hasDateRetired, Literal(r.date_retired, datatype=XSD.date)))

            # RDF: aliases
            # alias type code to URI mapping
            s2 = sql.SQL('''SELECT * FROM {dbschema}.address_alias WHERE principal_pid = {id}''')\
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            cursor.execute(s2)
            rows2 = cursor.fetchall()
            for row in rows2:
                r = config.reg(cursor, row)
                alias = BNode()
                g.add((alias, RDF.type, URIRef(LOOKUPS.alias_subclasses.get(r.alias_type_code))))
                g.add((a, GNAF.hasAlias, alias))
                g.add((alias, GNAF.aliasOf, URIRef(config.URI_ADDRESS_INSTANCE_BASE + str(r.alias_pid))))

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))


