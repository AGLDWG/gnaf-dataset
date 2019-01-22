# -*- coding: utf-8 -*-
from db import get_db_cursor
from model import GNAFModel, NotFoundError
from flask import render_template
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode, RDFS
import _config as config
from psycopg2 import sql


class AddressSite(GNAFModel):
    """
    This class represents an Address Site and methods in this class allow an Address Site to be loaded from the GNAF
    database and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, identifier, db_cursor=None):
        self.id = identifier
        self.uri = config.URI_ADDRESS_SITE_INSTANCE_BASE + identifier
        self.address_site_geocode_ids = dict()
        if db_cursor is not None:
            self.cursor = db_cursor
            self._cursor_context_manager = None
        else:
            self._cursor_context_manager = get_db_cursor()
            self.cursor = self._cursor_context_manager.__enter__()

    def __del__(self):
        if self._cursor_context_manager:
            self._cursor_context_manager.__exit__(None, None, None)

    def export_html(self, view='gnaf'):
        # connect to DB
        cursor = self.cursor

        if view == 'gnaf':
            s = sql.SQL('''SELECT
                a.address_type, a.address_site_name, gv.address_site_geocode_pid, gv.geocode_type                   
                FROM {dbschema}.address_site as a
                LEFT JOIN {dbschema}.address_site_geocode_view as gv on a.address_site_pid = gv.address_site_pid
                WHERE a.address_site_pid = {id};''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            cursor.execute(s)
            rows = cursor.fetchall()
            found = False
            for row in rows:
                found = True
                address_type = row[0]
                address_site_name = row[1]
                geocode_pid = row[2]
                if geocode_pid is not None:
                    self.address_site_geocode_ids[geocode_pid] = row[3].title()
            if not found:
                raise NotFoundError()
            #
            # s2 = sql.SQL('''SELECT
            #             address_site_geocode_pid,
            #             geocode_type
            #         FROM {dbschema}.address_site_geocode_view
            #         WHERE address_site_pid = {id}''') \
            #     .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            #
            # cursor.execute(s2)
            # rows = cursor.fetchall()
            # for row in rows:
            #     self.address_site_geocode_ids[row[0]] = row[1].title()

            view_html = render_template(
                'class_addressSite_gnaf.html',
                address_site_pid=self.id,
                address_site_name=address_site_name,
                address_type=address_type,
                address_site_geocode_ids=self.address_site_geocode_ids
            )

        elif view == 'ISO19160':
            view_html = render_template(
                'class_addressSite_ISO19160.html',
            )

        elif view == 'dct':
            s = sql.SQL('''SELECT 
                        address_type, 
                        address_site_name                       
                    FROM {dbschema}.address_site
                    WHERE address_site_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s)
            for record in cursor:
                address_type = record[0]
                address_site_name = record[1]
                break
            else:
                raise NotFoundError()

            view_html = render_template(
                'class_addressSite_dct.html',
                identifier=self.id,
                title='Address Site' + self.id,
                description=address_site_name,
                source='G-NAF, 2016',
                type='AddressSite'
            )
        else:
            return NotImplementedError("HTML representation of View '{}' is not implemented.".format(view))
        return view_html

    def export_rdf(self, view='ISO19160', format='text/turtle'):
        g = Graph()
        a = URIRef(self.uri)

        if view == 'ISO19160':
            # get the components from the DB needed for ISO19160
            s = sql.SQL('''SELECT 
                        address_type, 
                        address_site_name                       
                    FROM {dbschema}.address_site
                    WHERE address_site_pid = {id}''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))

            cursor = self.cursor
            # get just IDs, ordered, from the address_detail table, paginated by class init args
            cursor.execute(s)
            for record in cursor:
                address_type = record[0]
                address_site_name = record[1]
                break
            else:
                raise NotFoundError()


            AddressComponentTypeUriBase = 'http://def.isotc211.org/iso19160/-1/2015/Address/code/AddressComponentType/'

            ISO = Namespace('http://def.isotc211.org/iso19160/-1/2015/Address#')
            g.bind('iso19160', ISO)

            g.add((a, RDF.type, ISO.Address))

            ac_site_name = BNode()
            g.add((ac_site_name, RDF.type, ISO.AddressComponent))
            g.add((ac_site_name, ISO.valueInformation, Literal(address_site_name, datatype=XSD.string)))
            g.add((ac_site_name, ISO.type, URIRef(AddressComponentTypeUriBase + 'siteName')))
            g.add((a, ISO.addressComponent, ac_site_name))

        elif view == 'gnaf':
            GNAF = Namespace('http://linked.data.gov.au/def/gnaf#')
            g.bind('gnaf', GNAF)
            GEO = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geo', GEO)
            s = sql.SQL('''SELECT
                a.address_type, a.address_site_name, coa.uri, coa.preflabel, gc.address_site_geocode_pid, gc.geocode_type_code, gc.longitude, gc.latitude, cog.uri, cog.preflabel 
                FROM {dbschema}.address_site as a
                LEFT JOIN {dbschema}.address_site_geocode as gc on a.address_site_pid = gc.address_site_pid
                LEFT JOIN codes.address as coa on a.address_type = coa.code
                LEFT JOIN codes.geocode as cog on gc.geocode_type_code = cog.code
                WHERE a.address_site_pid = {id};''') \
                .format(id=sql.Literal(self.id), dbschema=sql.Identifier(config.DB_SCHEMA))
            cursor = self.cursor
            cursor.execute(s)
            rows = cursor.fetchall()
            found = False
            for row in rows:
                found = True
                address_type = row[0]
                address_site_name = row[1]
                address_type_uri = row[2]
                address_type_label = row[3]
                geocode_pid = row[4]
                if geocode_pid is not None:
                    self.address_site_geocode_ids[geocode_pid] = row[5]
                longitude = row[6]
                latitude = row[7]
                geocode_uri = row[8]
                geocode_preflabel = row[9]
            if not found:
                raise NotFoundError()
            g.add((a, RDF.type, GNAF.AddressSite))
            desc = 'AddressSite {}'.format(self.id)
            if address_site_name:
                desc = "{} \"{}\"".format(desc, address_site_name)
                g.add((a, RDFS.label, Literal(address_site_name, datatype=XSD.string)))
            if address_type and address_type_label:
                desc = "{} of {} type".format(desc, address_type_label)
            if address_type and address_type_uri:
                g.add((a, GNAF.gnafType, URIRef(address_type_uri)))
            else:
                g.add((a, GNAF.gnafType, URIRef("http://gnafld.net/def/gnaf/code/AddressTypes#Unknown")))
            g.add((a, RDFS.comment, Literal(desc, lang="en")))
            if geocode_uri or (latitude and longitude):
                geocode = BNode()
                g.add((geocode, RDF.type, GNAF.Geocode))
                if geocode_uri:
                    g.add((geocode, GNAF.gnafType, URIRef(geocode_uri)))
                if geocode_preflabel:
                    g.add((geocode, RDFS.label, Literal(geocode_preflabel, datatype=XSD.string)))
                if longitude and latitude:
                    g.add((geocode, GEO.asWKT,
                           Literal(self.make_wkt_literal(longitude=longitude, latitude=latitude),
                                   datatype=GEO.wktLiteral)))
                g.add((a, GEO.hasGeometry, geocode))
        elif view == 'dct':
            raise NotImplementedError("RDF Representation of the DCT View of an addressSite is not yet implemented.")
            # TODO: implement DCT RDF
        else:
            raise RuntimeError("Cannot render an RDF representation of that View.")
        return g
