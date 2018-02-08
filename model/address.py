from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
from psycopg2 import sql


class AddressRenderer(Renderer):
    """
    This class represents an Address and methods in this class allow an Address to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id, focus=False):
        # TODO: why doesn't this super thing work?
        # super(AddressRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_ADDRESS_INSTANCE_BASE + id

        # DB connection
        self.cursor = config.get_db_cursor()

        # get basic properties
        s = sql.SQL('''SELECT 
                    b.location_description,
                    b.street_locality_pid, 
                    b.locality_pid,                     
                    a.street_name, 
                    a.street_type_code, 
                    a.locality_name, 
                    a.state_abbreviation, 
                    b.postcode ,
                    a.latitude,
                    a.longitude,
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
                    CAST(b.number_first AS text), 
                    b.number_first_suffix,
                    b.number_last_prefix,
                    CAST(b.number_last AS text),
                    b.number_last_suffix,
                    b.alias_principal,
                    b.legal_parcel_id,
                    b.address_site_pid,
                    b.level_geocoded_code,
                    b.property_pid,
                    b.primary_secondary ,
                    u.uri, 
                    u.prefLabel,
                    u2.uri uri2,
                    u2.prefLabel prefLabel2                      
                FROM {dbschema}.address_view a 
                INNER JOIN {dbschema}.address_detail b ON a.address_detail_pid = b.address_detail_pid
                INNER JOIN {dbschema}.address_default_geocode g ON a.address_detail_pid = g.address_detail_pid                
                LEFT JOIN code_uris u ON g.geocode_type_code = u.code           
                LEFT JOIN code_uris u2 ON CAST(b.confidence AS text) = u2.code 
                WHERE u.vocab = 'Geocode'
                AND a.address_detail_pid = {id}''') \
            .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

        # get just IDs, ordered, from the address_detail table, paginated by class init args
        self.cursor.execute(s)
        for row in self.cursor.fetchall():
            r = config.reg(self.cursor, row)
            # assign this Address' instance variables
            self.description = r.location_description.title() if r.location_description is not None else None
            self.street_name = r.street_name.title()
            self.street_type = r.street_type_code
            self.locality_name = r.locality_name.title()
            self.state_territory = r.state_abbreviation
            self.postcode = r.postcode
            self.latitude = r.latitude
            self.longitude = r.longitude
            self.geocode_type_label = r.preflabel
            self.geocode_type_uri = r.uri
            self.confidence_uri = r.uri2
            self.confidence_prefLabel = r.preflabel2
            self.date_created = r.date_created
            self.date_last_modified = r.date_last_modified
            self.date_retired = r.date_retired
            self.building_name = r.building_name.title() if r.building_name is not None else None
            self.number_lot_prefix = r.lot_number_prefix
            self.number_lot = r.lot_number
            self.number_lot_suffix = r.lot_number_suffix
            self.flat_type_code = r.flat_type_code
            self.number_flat_prefix = r.flat_number_prefix
            self.number_flat = r.flat_number
            self.number_flat_suffix = r.flat_number_suffix
            self.level_type_code = r.level_type_code
            self.number_level_prefix = r.level_number_prefix
            self.number_level = r.level_number
            self.number_level_suffix = r.level_number_suffix
            self.number_first = r.number_first
            self.number_first_prefix = r.number_first_prefix
            self.number_first_suffix = r.number_first_suffix
            self.number_last_prefix = r.number_last_prefix
            self.number_last = r.number_last
            self.number_last_suffix = r.number_last_suffix
            self.alias_principal = r.alias_principal
            self.legal_parcel_id = r.legal_parcel_id
            self.address_site_pid = r.address_site_pid
            self.level_geocoded_code = r.level_geocoded_code
            self.property_pid = r.property_pid
            self.street_locality_pid = r.street_locality_pid
            self.locality_pid = r.locality_pid
            self.is_primary = True if r.primary_secondary == 'P' else False

            self.address_string, self.street_string = make_address_street_strings(
                level_type_code=r.level_type_code,
                level_number_prefix=r.level_number_prefix,
                level_number=r.level_number,
                level_number_suffix=r.level_number_suffix,
                flat_type_code=r.flat_type_code,
                flat_number_prefix=r.flat_number_prefix,
                flat_number=r.flat_number,
                flat_number_suffix=r.flat_number_suffix,
                number_first_prefix=r.number_first_prefix,
                number_first=r.number_first,
                number_first_suffix=r.number_first_suffix,
                number_last_prefix=r.number_last_prefix,
                number_last=r.number_last,
                number_last_suffix=r.number_last_suffix,
                building=r.building_name,
                lot_number_prefix=r.lot_number_prefix,
                lot_number=r.lot_number,
                lot_number_suffix=r.lot_number_suffix,
                street_name=r.street_name.title(),
                street_type=r.street_type_code,
                locality=r.locality_name.title(),
                state_territory=r.state_abbreviation,
                postcode=r.postcode
            )

        # get aliases
        self.alias_addresses = dict()
        s2 = sql.SQL('''SELECT alias_pid, uri, prefLabel 
                        FROM {dbschema}.address_alias 
                        LEFT JOIN code_uris ON {dbschema}.address_alias.alias_type_code = code_uris.code 
                        WHERE code_uris.vocab = 'Alias' AND principal_pid = {id}''') \
            .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
        self.cursor.execute(s2)
        for row in self.cursor.fetchall():
            r = config.reg(self.cursor, row)
            self.alias_addresses[r.alias_pid] = {
                'address_string': AddressRenderer(r.alias_pid, focus=False).address_string,
                'subclass_uri': r.uri,
                'subclass_label': r.preflabel  # note use of preflabel, not prefLabel: capital letter dies in reg
            }

        # get alternates for address if in focus
        if focus:
            # get principals
            self.principal_addresses = dict()
            s3 = sql.SQL('''SELECT principal_pid, uri, prefLabel  
                            FROM {dbschema}.address_alias 
                            LEFT JOIN code_uris ON {dbschema}.address_alias.alias_type_code = code_uris.code 
                            WHERE code_uris.vocab = 'Alias' AND alias_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            self.cursor.execute(s3)
            for row in self.cursor.fetchall():
                r = config.reg(self.cursor, row)
                a = AddressRenderer(r.principal_pid, focus=False)
                vocab_term = config.get_vocab_term('AliasSubclasses', r.alias_type_code)
                self.principal_addresses[r.principal_pid] = {
                    'address_string': a.address_string,
                    'subclass_uri': vocab_term[0],
                    'subclass_label': vocab_term[1]
                }

            # get primary
            self.primary_addresses = dict()
            s4 = sql.SQL('''SELECT primary_pid FROM {dbschema}.primary_secondary WHERE secondary_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            self.cursor.execute(s4)
            for row in self.cursor.fetchall():
                r = config.reg(self.cursor, row)
                a = AddressRenderer(r.primary_pid, focus=False)
                self.primary_addresses[r.primary_pid] = a.address_string

            # get secondaries
            self.secondary_addresses = dict()
            s5 = sql.SQL('''SELECT secondary_pid FROM {dbschema}.primary_secondary WHERE primary_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            self.cursor.execute(s5)
            rows = self.cursor.fetchall()
            for row in rows:
                r = config.reg(self.cursor, row)
                a = AddressRenderer(r.secondary_pid, focus=False)
                self.secondary_addresses[r.secondary_pid] = a.address_string

            # MBs
            self.mesh_block_2011s = {}
            self.mesh_block_2016s = {}
            s6 = sql.SQL('''SELECT 
                              mb_2011_code,
                              mb_2016_code, 
                              a.uri mb2011_uri, 
                              a.prefLabel mb2011_prefLabel,
                              b.uri mb2016_uri, 
                              b.prefLabel mb2016_prefLabel  
                            FROM gnaf.address_mesh_block_2016_view
                            INNER JOIN gnaf.address_mesh_block_2011_view 
                            ON {dbschema}.address_mesh_block_2016_view.address_detail_pid 
                            = {dbschema}.address_mesh_block_2011_view.address_detail_pid
                            LEFT JOIN code_uris a ON gnaf.address_mesh_block_2011_view.mb_match_code = a.code 
                            LEFT JOIN code_uris b ON gnaf.address_mesh_block_2016_view.mb_match_code = b.code 
                            WHERE a.vocab = 'MeshBlockMatch' 
                            AND b.vocab = 'MeshBlockMatch' 
                            AND {dbschema}.address_mesh_block_2016_view.address_detail_pid = {id};''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            self.cursor.execute(s6)
            for row in self.cursor.fetchall():
                r = config.reg(self.cursor, row)
                self.mesh_block_2011s[config.URI_MB_2011_INSTANCE_BASE + r.mb_2011_code] = {
                    'string': r.mb_2011_code,
                    'subclass_uri': r.mb2011_uri,
                    'subclass_label': r.mb2011_preflabel  # note use of preflabel, not prefLabel
                }
                self.mesh_block_2016s[config.URI_MB_2016_INSTANCE_BASE + r.mb_2016_code] = {
                    'string': r.mb_2016_code,
                    'subclass_uri': r.mb2016_uri,
                    'subclass_label': r.mb2016_preflabel  # note use of preflabel, not prefLabel
                }

    def render(self, view, format):
        if format == 'text/html':
            return self.export_html(view=view)
        else:
            return Response(self.export_rdf(view, format), mimetype=format)

    def export_html(self, view='gnaf'):
        if view == 'gnaf':
            view_html = render_template(
                'class_address_gnaf.html',
                address_string=self.address_string,
                address_detail_pid=self.id,
                street_name=self.street_name,
                street_type=self.street_type,
                locality_name=self.locality_name,
                state_territory=self.state_territory,
                postcode=self.postcode,
                latitude=self.latitude,
                longitude=self.longitude,
                geocode_type_label=self.geocode_type_label,
                geocode_type_uri=self.geocode_type_uri,
                confidence_uri=self.confidence_uri,
                confidence_prefLabel=self.confidence_prefLabel,
                geometry_wkt=make_wkt(self.longitude, self.latitude),
                date_created=self.date_created,
                date_last_modified=self.date_last_modified,
                date_retired=self.date_retired,
                building_name=self.building_name,
                number_lot_prefix=self.number_lot_prefix,
                number_lot=self.number_lot,
                number_lot_suffix=self.number_lot_suffix,
                flat_type_code=self.flat_type_code,
                number_flat_prefix=self.number_flat_prefix,
                number_flat=self.number_flat,
                number_flat_suffix=self.number_flat_suffix,
                level_type_code=self.level_type_code,
                number_level_prefix=self.number_level_prefix,
                number_level=self.number_level,
                number_level_suffix=self.number_level_suffix,
                number_first_prefix=self.number_first_prefix,
                number_first=self.number_first,
                number_first_suffix=self.number_first_suffix,
                number_last_prefix=self.number_last_prefix,
                number_last=self.number_last,
                number_last_suffix=self.number_last_suffix,
                alias_principal=self.alias_principal,
                legal_parcel_id=self.legal_parcel_id,
                address_site_pid=self.address_site_pid,
                level_geocoded_code=self.level_geocoded_code,
                property_pid=self.property_pid,
                street_locality_pid=self.street_locality_pid,
                locality_pid=self.locality_pid,
                alias_addresses=self.alias_addresses,
                principal_addresses=self.principal_addresses,
                secondary_addresses=self.secondary_addresses,
                primary_addresses=self.primary_addresses,
                mesh_block_2011_uri=config.URI_MB_2011_INSTANCE_BASE + '%s',
                mesh_block_2011s=self.mesh_block_2011s,
                mesh_block_2016_uri=config.URI_MB_2016_INSTANCE_BASE + '%s',
                mesh_block_2016s=self.mesh_block_2016s,
                street_string=self.street_string
            )

        elif view == 'ISO19160':
            s8 = sql.SQL('''SELECT longitude, latitude, c.name
                            FROM {dbschema}.address_site_geocode g 
                            INNER JOIN {dbschema}.address_detail det ON g.address_site_pid = det.address_site_pid
                            INNER JOIN {dbschema}.geocode_type_aut c ON g.geocode_type_code = c.code
                            WHERE address_detail_pid = {id}''').format(
                id=sql.Literal(self.id),
                dbschema=sql.Identifier(config.DB_SCHEMA)
            )
            self.cursor.execute(s8)
            positions = {}
            for row in self.cursor.fetchall():
                r = config.reg(self.cursor, row)
                positions[r.name] = make_wkt(r.longitude, r.latitude)

            view_html = render_template(
                'class_address_ISO19160.html',
                address_string=self.address_string,
                address_detail_pid=self.id,
                street_name=self.street_name,
                street_type=self.street_type,
                locality_name=self.locality_name,
                state_territory=self.state_territory,
                postcode=self.postcode,
                latitude=self.latitude,
                longitude=self.longitude,
                geocode_type=self.geocode_type,
                geocode_type_uri='http://broken.com',
                confidence=self.confidence,
                geometry_wkt=make_wkt(self.longitude, self.latitude),
                date_created=self.date_created,
                date_last_modified=self.date_last_modified,
                date_retired=self.date_retired,
                building_name=self.building_name,
                number_lot_prefix=self.number_lot_prefix,
                number_lot=self.number_lot,
                number_lot_suffix=self.number_lot_suffix,
                flat_type_code=self.flat_type_code,
                number_flat_prefix=self.number_flat_prefix,
                number_flat=self.number_flat,
                number_flat_suffix=self.number_flat_suffix,
                level_type_code=self.level_type_code,
                number_level_prefix=self.number_level_prefix,
                number_level=self.number_level,
                number_level_suffix=self.number_level_suffix,
                number_first_prefix=self.number_first_prefix,
                number_first=self.number_first,
                number_first_suffix=self.number_first_suffix,
                number_last_prefix=self.number_last_prefix,
                number_last=self.number_last,
                number_last_suffix=self.number_last_suffix,
                alias_principal=self.alias_principal,
                legal_parcel_id=self.legal_parcel_id,
                address_site_pid=self.address_site_pid,
                level_geocoded_code=self.level_geocoded_code,
                property_pid=self.property_pid,
                street_locality_pid=self.street_locality_pid,
                locality_pid=self.locality_pid,
                alias_addresses=self.alias_addresses,
                principal_addresses=self.principal_addresses,
                secondary_addresses=self.secondary_addresses,
                primary_addresses=self.primary_addresses,
                mesh_block_2011_uri=config.URI_MB_2011_INSTANCE_BASE + '%s',
                mesh_block_2011s=self.mesh_block_2011s,
                mesh_block_2016_uri=config.URI_MB_2016_INSTANCE_BASE + '%s',
                mesh_block_2016s=self.mesh_block_2016s,
                street_string=self.street_string,
                positions=positions
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

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            self.cursor.execute(s)
            for record in self.cursor:
                address_string = '{} {} {}, {}, {} {}' \
                    .format(record[2], record[3].title(), record[4].title(), record[5].title(), record[6], record[7])
                coverage_wkt = make_wkt(r.longitude, r.latitude)

            view_html = render_template(
                'class_address_dct.html',
                identifier=self.id,
                title='Address ' + self.id,
                description=address_string,
                coverage=coverage_wkt,
                source='G-NAF, 2016',
                type='Address'
            )

        return render_template(
            'class_address.html',
            view_html=view_html,
            address_id=self.id,
            address_uri=self.uri,
        )

    def export_rdf(self, view='gnaf', format='text/turtle'):
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

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            self.cursor.execute(s)
            for record in self.cursor:
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

            if ac_level_type_value is not None:
                ac_level_type = BNode()
                g.add((ac_level_type, RDF.type, ISO.AddressComponent))
                g.add((ac_level_type, ISO.valueInformation, Literal(ac_level_type_value, datatype=XSD.string)))
                g.add((ac_level_type, ISO.type, URIRef(AddressComponentTypeUriBase + 'levelType')))
                g.add((ac_level, ISO.valueComponent, ac_level_type))

            if ac_level_number_value is not None:
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
            g.add((geometry, GEO.asWKT, Literal(make_wkt(r.longitude, r.latitude), datatype=GEO.wktLiteral)))

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

            GNAF = Namespace('http://gnafld.org/def/gnaf#')
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

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            self.cursor.execute(s)
            rows = self.cursor.fetchall()
            for row in rows:
                r = config.reg(self.cursor, row)

                # RDF: geometry
                geocode = BNode()
                g.add((geocode, RDF.type, URIRef(self.geocode_type_uri)))
                g.add((geocode, RDFS.label, Literal(self.geocode_type_label, datatype=XSD.string)))
                g.add((geocode, GEO.asWKT, Literal(make_wkt(r.longitude, r.latitude), datatype=GEO.wktLiteral)))
                g.add((a, GEO.hasGeometry, geocode))

                if r.private_street is not None:
                    g.add((a, GNAF.hasPrivateStreet, Literal(True, datatype=XSD.boolean)))
                else:
                    g.add((a, GNAF.hasPrivateStreet, Literal(False, datatype=XSD.boolean)))

                g.add((a, GNAF.hasStreet, URIRef(config.URI_STREET_INSTANCE_BASE + str(r.street_locality_pid))))

                g.add((a, GNAF.hasGnafConfidence, URIRef(self.confidence_uri)))
                g.add((URIRef(self.confidence_uri), RDFS.label, Literal(self.confidence_prefLabel, datatype=XSD.string)))

                if r.address_site_pid is not None:
                    g.add((a, GNAF.hasAddressSite, URIRef(config.URI_ADDRESS_SITE_INSTANCE_BASE + str(r.address_site_pid))))

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
                if self.description is not None:
                    g.add((a, DCT.description, Literal(self.description, datatype=XSD.string)))

                g.add((a, GNAF.hasPostcode, Literal(self.postcode, datatype=XSD.integer)))

                if self.building_name is not None:
                    g.add((a, GNAF.hasBuldingName, Literal(self.building_name, datatype=XSD.string)))

                g.add((a, GNAF.hasDateCreated, Literal(self.date_created, datatype=XSD.date)))
                g.add((a, GNAF.hasDateLastModified, Literal(self.date_last_modified, datatype=XSD.date)))
                if self.date_retired is not None:
                    g.add((a, GNAF.hasDateRetired, Literal(self.date_retired, datatype=XSD.date)))

                print(len(self.alias_addresses))
                for k, v in self.alias_addresses.items():
                    a = BNode()
                    g.add((URIRef(self.uri), GNAF.hasAlias, a))
                    g.add((a, RDF.type, URIRef(v['subclass_uri'])))
                    g.add((a, RDFS.label, Literal(v['subclass_label'], datatype=XSD.string)))
                    g.add((a, GNAF.aliasOf, URIRef(config.URI_ADDRESS_INSTANCE_BASE + k)))
            # RDF: aliases
            # # alias type code to URI mapping
            # s2 = sql.SQL('''SELECT * FROM {dbschema}.address_alias WHERE principal_pid = {id}''')\
            #     .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            # self.cursor.execute(s2)
            # for row in self.cursor.fetchall():
            #     r = config.reg(self.cursor, row)
            #     alias = BNode()
            #     g.add((alias, RDF.type, URIRef(LOOKUPS.alias_subclasses.get(r.alias_type_code))))
            #     g.add((a, GNAF.hasAlias, alias))
            #     g.add((alias, GNAF.aliasOf, URIRef(config.URI_ADDRESS_INSTANCE_BASE + str(r.alias_pid))))

            # for k, v in self.alias_addresses:
            #     print('hello')
                # a = BNode()
                # g.add((a, RDF.type, v['subclass_uri']))
                # g.add((a, GNAF.hasAlias, URIRef(config.URI_ADDRESS_INSTANCE_BASE + str(k))))
                # g.add((a, GNAF.aliasOf, URIRef(self.uri)))

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))


# static methods
def make_address_street_strings(
        level_type_code=None,
        level_number_prefix=None,
        level_number=None,
        level_number_suffix=None,
        flat_type_code=None,
        flat_number_prefix=None,
        flat_number=None,
        flat_number_suffix=None,
        number_first_prefix=None,
        number_first=None,
        number_first_suffix=None,
        number_last_prefix=None,
        number_last=None,
        number_last_suffix=None,
        building=None,
        lot_number_prefix=None,
        lot_number=None,
        lot_number_suffix=None,
        street_name=None,
        street_type=None,
        street_suffix_code=None,
        locality=None,
        state_territory=None,
        postcode=None):
        street_string = '{} {} {}'.format(
            street_name,
            street_type.title(),
            street_suffix_code if street_suffix_code is not None else ''
        )
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
                    address_string += '{} {} '.format(
                        flat_type_code.title(),
                        flat_num
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
                address_string += 'LOT {} '.format(lot_num)

            address_string += '{st}, {loc}, {state} {postcode}'.format(
                st=street_string,
                loc=locality,
                state=state_territory,
                postcode=postcode
            )

        return address_string, street_string


def make_wkt(longitude, latitude):
    return '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(
        longitude, latitude
    )
