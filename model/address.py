from model.renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI, LdapiParameterError
from psycopg2 import sql
import json
import decimal


class AddressRenderer(Renderer):
    """
    This class represents an Address and methods in this class allow an Address to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id, focus=False, db_cursor=None):
        # TODO: why doesn't this super thing work?
        # super(AddressRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_ADDRESS_INSTANCE_BASE + id

        # DB connection
        if db_cursor is not None:
            self.cursor = db_cursor
        else:
            self.cursor = config.get_db_cursor()

        # get basic properties
        s = sql.SQL('''SELECT 
                            d.location_description,
                            d.street_locality_pid, 
                            s.street_name, 
                            s.street_type_code, 
                            d.locality_pid,
                            l.locality_name, 
                            l.locality_class_code,
                            TRIM(BOTH '0123456789' FROM d.locality_pid) state_abbreviation,
                            d.postcode,
                            g.latitude,
                            g.longitude,
                            CAST(d.date_created AS text),
                            CAST(d.date_last_modified AS text),
                            CAST(d.date_retired AS text),
                            d.building_name,
                            d.lot_number_prefix,
                            d.lot_number,
                            d.lot_number_suffix,
                            d.flat_type_code,
                            d.flat_number_prefix,
                            CAST(d.flat_number AS text),
                            d.flat_number_suffix,
                            d.level_type_code,
                            d.level_number_prefix,
                            CAST(d.level_number AS text),
                            d.level_number_suffix,
                            d.number_first_prefix,
                            CAST(d.number_first AS text), 
                            d.number_first_suffix,
                            d.number_last_prefix,
                            CAST(d.number_last AS text),
                            d.number_last_suffix,
                            d.alias_principal,
                            d.legal_parcel_id,
                            d.address_site_pid,
                            d.level_geocoded_code,
                            d.property_pid,
                            d.primary_secondary ,
                            u.uri, 
                            u.prefLabel,
                            u2.uri uri2,
                            u2.prefLabel prefLabel2,
                            u3.uri uri3,
                            u3.prefLabel prefLabel3,
                            u4.uri uri4,
                            u4.prefLabel prefLabel4,
                            u5.uri uri5,
                            u5.prefLabel prefLabel5,
                            u6.uri uri6,
                            u6.prefLabel prefLabel6                                               
                            FROM gnaf.address_detail d
                            INNER JOIN gnaf.street_locality s ON d.street_locality_pid = s.street_locality_pid
                            INNER JOIN gnaf.locality l ON d.locality_pid = l.locality_pid
                            INNER JOIN gnaf.address_default_geocode g ON d.address_detail_pid = g.address_detail_pid                
                            LEFT JOIN codes.geocode u ON g.geocode_type_code = u.code           
                            LEFT JOIN codes.gnafconfidence u2 ON CAST(d.confidence AS text) = u2.code 
                            LEFT JOIN codes.locality u3 ON l.locality_class_code = u3.code 
                            INNER JOIN gnaf.address_site a ON d.address_site_pid = a.address_site_pid
                            LEFT JOIN codes.address u4 ON a.address_type = u4.code 
                            LEFT JOIN codes.flat u5 ON d.flat_type_code = u5.code 
                            LEFT JOIN codes.state u6 ON TRIM(BOTH '0123456789' FROM d.locality_pid) = u6.code 
                            WHERE d.address_detail_pid = {id};
                            ''').format(id=sql.Literal(self.id))

        # get just IDs, ordered, from the address_detail table, paginated by class init args
        self.cursor.execute(s)
        for row in self.cursor.fetchall():
            r = config.reg(self.cursor, row)
            # assign this Address' instance variables
            self.address_subclass_uri = r.uri4
            self.address_subclass_label = r.preflabel4
            self.description = r.location_description.title() if r.location_description is not None else None
            self.street_name = r.street_name.title()
            self.street_type = r.street_type_code
            self.locality_name = r.locality_name.title()
            self.state_territory = r.state_abbreviation
            self.state_uri = r.uri6
            self.state_prefLabel = r.preflabel6
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
            # self.private_street = True r.private_street private street seemingly unused in address_detail
            self.is_primary = True if r.primary_secondary == 'P' else False

            self.address_string, self.street_string = make_address_street_strings(
                level_type_code=self.level_type_code,
                level_number_prefix=self.number_level_prefix,
                level_number=self.number_level,
                level_number_suffix=self.number_level_suffix,
                flat_type_code=self.flat_type_code,
                flat_number_prefix=self.number_flat_prefix,
                flat_number=self.number_flat,
                flat_number_suffix=self.number_flat_suffix,
                number_first_prefix=self.number_first_prefix,
                number_first=self.number_first,
                number_first_suffix=self.number_first_suffix,
                number_last_prefix=self.number_last_prefix,
                number_last=self.number_last,
                number_last_suffix=self.number_last_suffix,
                building=self.building_name,
                lot_number_prefix=self.number_lot_prefix,
                lot_number=self.number_lot,
                lot_number_suffix=self.number_lot_suffix,
                street_name=self.street_name,
                street_type=self.street_type,
                locality=self.locality_name,
                state_territory=self.state_territory,
                postcode=self.postcode
            )

        # get aliases
        self.alias_addresses = dict()
        s2 = sql.SQL('''SELECT alias_pid, uri, prefLabel 
                        FROM gnaf.address_alias 
                        LEFT JOIN codes.alias ON gnaf.address_alias.alias_type_code = codes.alias.code 
                        WHERE principal_pid = {id}''') \
            .format(id=sql.Literal(self.id))
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
                            FROM gnaf.address_alias 
                            LEFT JOIN codes.alias ON gnaf.address_alias.alias_type_code = codes.alias.code 
                            WHERE alias_pid = {id}''') \
                .format(id=sql.Literal(self.id))
            self.cursor.execute(s3)
            for row in self.cursor.fetchall():
                r = config.reg(self.cursor, row)
                ar = AddressRenderer(r.principal_pid, focus=False)
                self.principal_addresses[r.principal_pid] = {
                    'address_string': ar.address_string,
                    'subclass_uri': r.uri,
                    'subclass_label': r.preflabel
                }

            # get primary
            self.primary_addresses = dict()
            s4 = sql.SQL('''SELECT primary_pid FROM gnaf.primary_secondary WHERE secondary_pid = {id}''') \
                .format(id=sql.Literal(self.id))
            self.cursor.execute(s4)
            for row in self.cursor.fetchall():
                r = config.reg(self.cursor, row)
                a = AddressRenderer(r.primary_pid, focus=False)
                self.primary_addresses[r.primary_pid] = a.address_string

            # get secondaries
            self.secondary_addresses = dict()
            s5 = sql.SQL('''SELECT secondary_pid FROM gnaf.primary_secondary WHERE primary_pid = {id}''') \
                .format(id=sql.Literal(self.id))
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
                            ON gnaf.address_mesh_block_2016_view.address_detail_pid 
                            = gnaf.address_mesh_block_2011_view.address_detail_pid
                            LEFT JOIN codes.meshblockmatch a ON gnaf.address_mesh_block_2011_view.mb_match_code = a.code 
                            LEFT JOIN codes.meshblockmatch b ON gnaf.address_mesh_block_2016_view.mb_match_code = b.code 
                            WHERE gnaf.address_mesh_block_2016_view.address_detail_pid = {id};''') \
                .format(id=sql.Literal(self.id))

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
        if view == 'schemaorg':
            return Response(self.export_schemaorg(), mimetype='application/ld+json')
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
                geometry_wkt=self.make_wkt_literal(longitude=self.longitude, latitude=self.latitude),
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
                schemaorg=self.export_schemaorg()
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
                     WHERE address_detail_pid = {id}''') \
                .format(id=sql.Literal(self.id))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            self.cursor.execute(s)
            for record in self.cursor:
                address_string = '{} {} {}, {}, {} {}' \
                    .format(record[2], record[3].title(), record[4].title(), record[5].title(), record[6], record[7])
                coverage_wkt = self.make_wkt_literal(longitude=self.longitude, latitude=self.latitude)

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

    def exp_19160_Address(self, g):
        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)
        g.add((URIRef(self.uri), RDF.type, ISO.Address))
        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.id'),
            URIRef(self.uri)  # always using this
        ))
        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.class'),
            URIRef('http://gnafld.net/def/gnaf#Address')  # always using this
        ))

        # TODO: support all Address Lifecycle Stages: current, proposed, rejected, reserved, retired, unknown
        if self.date_retired is not None:
            life_cycle_stage = 'retired'
        else:
            life_cycle_stage = 'current'
        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.lifecycleStage'),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressLifecycleStage/'
                   + life_cycle_stage)
        ))

        # TODO: confirm all G-Naf addresses are official
        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.status'),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressStatus/official')
        ))

    def exp_19160_AddressPosition(self, g):
        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)
        GEO = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', GEO)

        geom = BNode()
        g.add((geom, RDF.type, GEO.Geometry))
        g.add((geom, RDF.type, ISO.GM_Object))  # thus equating the 19160 GM_Object with a geo:Geometry
        g.add((geom, GEO.asGML, Literal(make_gml_literal(self.longitude, self.latitude), datatype=GEO.gmlLiteral)))

        pos = BNode()
        g.add((pos, RDF.type, ISO.AddressPosition))  # inferred to be a geo:Feature
        g.add((
            pos,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressPosition.geometry'),
            geom
        ))
        g.add((pos, GEO.hasGeometry, geom))  # due to equating the 19160 GM_Object with a geo:Geometry
        g.add((
            pos,
            ISO.type,
            URIRef(self.geocode_type_uri)  # ISO19160 offers no codes for this so we use GNAF codes
        ))
        g.add((URIRef(self.uri), ISO.position, pos))

    def exp_19160_AddressComponent(self, g, ac_type, acv_value, acv_type='defaultValue'):
        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)
        ac_type_base = 'http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressComponentType/'
        ac_value_type_base = \
            'http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressComponentValueType/'

        acv = BNode()
        g.add((acv, RDF.type, ISO.AddressComponentValue))
        g.add((
            acv,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponentValue.type'),
            URIRef(ac_value_type_base + acv_type)
        ))
        # choose datatype based on AddressComponent.type
        dt = {
            'addressedObjectIdentifer': 'http://www.w3.org/2001/XMLSchema#string',
            'administrativeAreaName': 'http://www.w3.org/2001/XMLSchema#string',
            'thoroughfareName': 'http://www.w3.org/2001/XMLSchema#string',
            'localityName': 'http://www.w3.org/2001/XMLSchema#string',
            'postOfficeName': 'http://www.w3.org/2001/XMLSchema#string',
            'postcode': 'http://www.w3.org/2001/XMLSchema#integer',
            'countryName': 'http://www.w3.org/2001/XMLSchema#string',
            'countryCode': 'http://www.w3.org/2001/XMLSchema#string'
        }
        g.add((
            acv,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponentValue.value'),
            Literal(acv_value, datatype=dt.get(ac_type))
        ))

        ac = BNode()
        g.add((ac, RDF.type, ISO.AddressComponent))
        g.add((
            ac,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponent.type'),
            URIRef(ac_type_base + ac_type)
        ))
        g.add((
            ac,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponent.valueInformation'),
            acv
        ))

        if ac_type == 'thoroughfareName':
            g.add((
                ac,
                URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponent.references'),
                URIRef(config.URI_STREETLOCALITY_INSTANCE_BASE + self.street_locality_pid)
            ))
        elif ac_type == 'localityName':
            g.add((
                ac,
                URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponent.references'),
                URIRef(config.URI_LOCALITY_INSTANCE_BASE + self.locality_pid)
            ))
        elif ac_type == 'administrativeAreaName':
            g.add((
                ac,
                URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponent.references'),
                URIRef(self.state_uri)
            ))

        elif ac_type == 'countryCode':
            g.add((
                ac,
                URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressComponent.references'),
                URIRef('http://www.geonames.org/2077456')  # Australia
            ))

        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.addressComponent'),
            ac
        ))

        return ac

    def exp_19160_AddressAlias(self, g, alias_uri_str):
        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)

        aa = BNode()
        g.add((aa, RDF.type, ISO.AddressAlias))
        g.add((
            aa,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressAlias.type'),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/'
                   'AddressComponentType/unspecifiedAlias')  # TODO: extend the ISO codelist to include GNAF alias types
        ))
        g.add((
            aa,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressAlias.address'),
            URIRef(alias_uri_str)
        ))

        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.alias'),
            aa
        ))

    def exp_19160_AddressProvenance(self, g):
        ORG = Namespace('http://www.w3.org/ns/org#')
        g.bind('org', ORG)

        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)

        org = URIRef('https://www.psma.com.au')
        g.add((org, RDF.type, ORG.Organization))

        prov = BNode()
        g.add((prov, RDF.type, ISO.AddressProvenance))

        # g.add((
        #     prov,
        #     URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressProvenance.authority'),
        #     org
        # ))

        g.add((
            prov,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressProvenance.owner'),
            org
        ))

        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.provenance'),
            prov
        ))

    def exp_19160_AddressedPeriod(self, g):
        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)

        ap = BNode()
        g.add((ap, RDF.type, ISO.AddressedPeriod))

        g.add((
            ap,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressPeriod.addressedFrom'),
            Literal(self.date_created, datatype=XSD.date)
        ))

        if self.date_retired is not None:
            g.add((
                ap,
                URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressPeriod.addressedTo'),
                Literal(self.date_retired, datatype=XSD.date)
            ))

        return ap

    def exp_19160_AddressableObject(self, g):
        ISO = Namespace('http://reference.data.gov.au/def/ont/iso19160-1-address#')
        g.bind('iso19160', ISO)

        ao = BNode()
        subclass = self.address_subclass_label.replace(' ', '').replace('Address', '')
        g.add((
            ao,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#AddressableObject.type'),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address/Address/code/AddressableObjectType/' +
                   subclass)
        ))

        g.add((
            ao,
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.theAddressedPeriod'),
            self.exp_19160_AddressedPeriod(g)
        ))

        g.add((
            URIRef(self.uri),
            URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.addressedObject'),
            ao
        ))

    def export_rdf(self, view='gnaf', format='text/turtle'):
        g = Graph()

        if view == 'ISO19160':
            self.exp_19160_Address(g)

            self.exp_19160_AddressableObject(g)

            ac_id_list = []

            if self.building_name is not None:
                ac_id_list.append(self.exp_19160_AddressComponent(g, 'addressedObjectIdentifier', self.building_name))

            if self.number_flat is not None:
                flat = str(self.number_flat)
                if self.number_flat_prefix is not None:
                    flat = self.number_flat_prefix + ' ' + flat
                if self.number_flat_suffix is not None:
                    flat = flat + ' ' + self.number_flat_suffix
                flat = 'Unit ' + flat
                ac_id_list.append(self.exp_19160_AddressComponent(g, 'addressedObjectIdentifier', flat))

            if self.number_level is not None:
                level = str(self.number_level)
                if self.number_level_prefix is not None:
                    level = self.number_level_prefix + ' ' + level
                if self.number_level_suffix is not None:
                    level = level + ' ' + self.number_level_suffix
                level = 'Level ' + level
                ac_id_list.append(self.exp_19160_AddressComponent(g, 'addressedObjectIdentifier', level))

            if self.number_lot is not None:
                lot = str(self.number_lot)
                if self.number_lot_prefix is not None:
                    lot = self.number_lot_prefix + ' ' + lot
                if self.number_lot_suffix is not None:
                    lot = lot + ' ' + self.number_lot_suffix
                lot = 'Lot ' + lot
                ac_id_list.append(self.exp_19160_AddressComponent(g, 'addressedObjectIdentifier', lot))

            if self.number_first is not None:
                num = str(self.number_first)
                if self.number_first_prefix is not None:
                    num = self.number_first_prefix + ' ' + num
                if self.number_first_suffix is not None:
                    num = num + ' ' + self.number_first_suffix

                if self.number_last is not None:
                    num_last = str(self.number_last)
                    if self.number_last_prefix is not None:
                        num_last = self.number_last_prefix + ' ' + num_last
                    if self.number_last_suffix is not None:
                        num_last = num_last + ' ' + self.number_last_suffix
                    num = num + '-' + num_last
                ac_id_list.append(self.exp_19160_AddressComponent(g, 'addressedObjectIdentifier', num))

            # order for all the addressedObjectIdentifier ACs
            OLO = Namespace('http://purl.org/ontology/olo/core#')
            g.bind('olo', OLO)
            if len(ac_id_list) > 0:
                ord = BNode()
                g.add((ord, RDF.type, OLO.OrderedList))
                g.add((ord, OLO.length, Literal(len(ac_id_list), datatype=XSD.integer)))
                for idx, val in enumerate(ac_id_list):
                    s = BNode()
                    g.add((s, URIRef('http://purl.org/ontology/olo/core#index'), Literal(idx, datatype=XSD.positiveInteger)))
                    g.add((s, OLO.item, val))
                    g.add((ord, OLO.slot, s))

            self.exp_19160_AddressComponent(g, 'thoroughfareName', self.street_string, acv_type='abbreviatedAlternative')

            self.exp_19160_AddressComponent(g, 'localityName', self.locality_name)

            self.exp_19160_AddressComponent(
                g, 'administrativeAreaName', self.state_territory, acv_type='abbreviatedAlternative'
            )

            self.exp_19160_AddressComponent(g, 'postcode', self.postcode)

            self.exp_19160_AddressComponent(g, 'countryName', 'Australia')

            self.exp_19160_AddressComponent(g, 'countryCode', 'AUS')

            self.exp_19160_AddressPosition(g)

            self.exp_19160_AddressProvenance(g)

            if hasattr(self, 'alias_addresses'):
                for k, v in self.alias_addresses.items():
                    self.exp_19160_AddressAlias(g, config.URI_ADDRESS_INSTANCE_BASE + k)

            if hasattr(self, 'primary_addresses'):
                for k, v in self.primary_addresses.items():
                    g.add((
                        URIRef(self.uri),
                        URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.parentAddress'),
                        URIRef(config.URI_ADDRESS_INSTANCE_BASE + k)
                    ))

            if hasattr(self, 'secondary_addresses'):
                for k, v in self.secondary_addresses.items():
                    g.add((
                        URIRef(self.uri),
                        URIRef('http://reference.data.gov.au/def/ont/iso19160-1-address#Address.childAddress'),
                        URIRef(config.URI_ADDRESS_INSTANCE_BASE + k)
                    ))

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

            a = URIRef(self.uri)

            # RDF: declare Address instance
            g.add((a, RDF.type, GNAF.Address))
            g.add((a, GNAF.gnafType, URIRef(self.address_subclass_uri)))
            g.add((a, RDFS.label,
                   Literal('Address ' + self.id + ' of ' + self.address_subclass_label + ' type', datatype=XSD.string)))

            # RDF: geometry
            geocode = BNode()
            g.add((geocode, RDF.type, GNAF.Geocode))
            g.add((geocode, GNAF.gnafType, URIRef(self.geocode_type_uri)))
            g.add((geocode, RDFS.label, Literal(self.geocode_type_label, datatype=XSD.string)))
            g.add((geocode, GEO.asWKT,
                   Literal(self.make_wkt_literal(
                       longitude=self.longitude, latitude=self.latitude
                   ), datatype=GEO.wktLiteral)))
            g.add((a, GEO.hasGeometry, geocode))

            # g.add((a, GNAF.hasPrivateStreet,
            # Literal(True if self.private_street is not None else False, datatype=XSD.boolean)))
            g.add((a, GNAF.hasStreet, URIRef(config.URI_STREETLOCALITY_INSTANCE_BASE + str(self.street_locality_pid))))

            g.add((a, GNAF.hasGnafConfidence, URIRef(self.confidence_uri)))
            g.add((URIRef(self.confidence_uri), RDFS.label, Literal(self.confidence_prefLabel, datatype=XSD.string)))

            if self.address_site_pid is not None:
                g.add((a, GNAF.hasAddressSite,
                       URIRef(config.URI_ADDRESS_SITE_INSTANCE_BASE + str(self.address_site_pid))))

            # RDF: Numbers
            # lot_number
            if self.number_lot is not None:
                lot_number = BNode()
                g.add((lot_number, RDF.type, GNAF.Number))
                g.add((lot_number, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/NumberTypes#Lot')))
                g.add((lot_number, PROV.value, Literal(str(self.number_lot), datatype=XSD.integer)))
                g.add((a, GNAF.hasNumber, lot_number))
                if self.number_lot_prefix is not None:
                    g.add((lot_number, GNAF.hasPrefix, Literal(str(self.number_lot_prefix), datatype=XSD.string)))
                if self.number_lot_suffix is not None:
                    g.add((lot_number, GNAF.hasSuffix, Literal(str(self.number_lot_suffix), datatype=XSD.string)))

            # TODO: represent flat_type_code

            # flat_number
            if self.number_flat is not None:
                flat_number = BNode()
                g.add((flat_number, RDF.type, GNAF.Number))
                g.add((flat_number, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/NumberTypes#Flat')))
                g.add((flat_number, PROV.value, Literal(int(self.number_flat), datatype=XSD.integer)))
                g.add((a, GNAF.hasNumber, flat_number))
                if self.number_flat_prefix is not None:
                    g.add((flat_number, GNAF.hasPrefix, Literal(str(self.number_flat_prefix), datatype=XSD.string)))
                if self.number_flat_suffix is not None:
                    g.add((flat_number, GNAF.hasSuffix, Literal(str(self.number_flat_suffix), datatype=XSD.string)))
            # level_number
            if self.number_level is not None:
                level_number = BNode()
                g.add((level_number, RDF.type, GNAF.Number))
                g.add((level_number, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/NumberTypes#Level')))
                g.add((level_number, PROV.value, Literal(int(self.number_level), datatype=XSD.integer)))
                g.add((a, GNAF.hasNumber, level_number))
                if self.number_level_prefix is not None:
                    g.add((level_number, GNAF.hasPrefix, Literal(str(self.number_level_prefix), datatype=XSD.string)))
                if self.number_level_suffix is not None:
                    g.add((level_number, GNAF.hasSuffix, Literal(str(self.number_level_suffix), datatype=XSD.string)))
            # number_first
            if self.number_first is not None:
                number_first = BNode()
                g.add((number_first, RDF.type, GNAF.Number))
                g.add((number_first, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/NumberTypes#FirstStreet')))
                g.add((number_first, PROV.value, Literal(int(self.number_first), datatype=XSD.integer)))
                g.add((a, GNAF.hasNumber, number_first))
                if self.number_first_prefix is not None:
                    g.add((number_first, GNAF.hasPrefix, Literal(str(self.number_first_prefix), datatype=XSD.string)))
                if self.number_first_suffix is not None:
                    g.add((number_first, GNAF.hasSuffix, Literal(str(self.number_first_suffix), datatype=XSD.string)))
            # number_last
            if self.number_last is not None:
                number_last = BNode()
                g.add((number_last, RDF.type, GNAF.Number))
                g.add((number_last, GNAF.gnafType, URIRef('http://gnafld.net/def/gnaf/code/NumberTypes#LastStreet')))
                g.add((number_last, PROV.value, Literal(int(self.number_last), datatype=XSD.integer)))
                g.add((a, GNAF.hasNumber, number_last))
                if self.number_last_prefix is not None:
                    g.add((number_last, GNAF.hasPrefix, Literal(str(self.number_last_prefix), datatype=XSD.string)))
                if self.number_last_suffix is not None:
                    g.add((number_last, GNAF.hasSuffix, Literal(str(self.number_last_suffix), datatype=XSD.string)))

            # RDF: locality
            g.add((a, GNAF.hasLocality, URIRef(config.URI_LOCALITY_INSTANCE_BASE + self.locality_pid)))

            g.add((a, GNAF.hasState, URIRef(self.state_uri)))
            g.add((URIRef(self.state_uri), RDFS.label, Literal(self.state_prefLabel, datatype=XSD.string)))

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

            if hasattr(self, 'alias_addresses'):
                for k, v in self.alias_addresses.items():
                    a = BNode()
                    g.add((a, RDF.type, GNAF.Alias))
                    g.add((URIRef(self.uri), GNAF.hasAlias, a))
                    g.add((a, GNAF.gnafType, URIRef(v['subclass_uri'])))
                    g.add((a, RDFS.label, Literal(v['subclass_label'], datatype=XSD.string)))
                    g.add((a, GNAF.aliasOf, URIRef(config.URI_ADDRESS_INSTANCE_BASE + k)))

            if hasattr(self, 'primary_addresses'):
                for k, v in self.primary_addresses.items():
                    g.add((URIRef(self.uri), GNAF.hasAddressPrimary, URIRef(config.URI_ADDRESS_INSTANCE_BASE + k)))
                    # g.add((URIRef(k), RDFS.label, Literal(v, datatype=XSD.string)))

            if hasattr(self, 'secondary_addresses'):
                for k, v in self.secondary_addresses.items():
                    g.add((URIRef(self.uri), GNAF.hasAddressSecondary, URIRef(config.URI_ADDRESS_INSTANCE_BASE + k)))
                    # g.add((URIRef(k), RDFS.label, Literal(v, datatype=XSD.string)))

        elif view == 'dct':
            pass
            # TODO: implement DCT RDF

        else:
            raise LdapiParameterError('_view unknown')

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))

    def export_schemaorg(self):
        data = {
            '@context': 'http://schema.org',
            '@type': 'Place',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': self.address_string.split(',')[0],
                'addressLocality': self.locality_name,
                'addressRegion': self.state_prefLabel,
                'postalCode': self.postcode,
                'addressCountry': 'AU'
            },
            'geo': {
                '@type': 'GeoCoordinates',
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'name': 'Geocoded Address ' + self.id
        }

        return json.dumps(data, cls=DecimalEncoder)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


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
        street_string = '{}{}{}'.format(
            street_name,
            ' ' + street_type.title() if street_type is not None else '',
            ' ' + street_suffix_code if street_suffix_code is not None else ''
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


def make_gml_literal(longitude, latitude):
    return \
            '<gml:Point \n' +\
            '\tsrsName="http://www.opengis.net/def/crs/OGC/1.3/CRS84"\n' +\
            '\txmlns:gml="http://www.opengis.net/gml">\n' +\
            '\t<gml:posList srsDimension="2">{} {}</gml:posList>\n' +\
            '</gml:Point>'.format(
                longitude, latitude
            )


if __name__ == '__main__':
    a = AddressRenderer('GANSW703902211', focus=True)
    print(a.export_rdf().decode('utf-8'))

# has alias for which it can't get address subclass: GAACT715069724. Alias is GAACT718348352
# GAACT718348352 has subclass UnknownVillaAddress
