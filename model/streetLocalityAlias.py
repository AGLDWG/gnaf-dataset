from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi.ldapi import LDAPI
import psycopg2
from psycopg2 import sql


class StreetLocalityAliasRenderer(Renderer):
    """
    This class represents an Street Locality Alias and methods in this class allow an Street Locality Alias to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id):
        # TODO: why doesn't this super thing work?
        # super(StreetLocalityAliasRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_STREET_LOCALITY_ALIAS_INSTANCE_BASE + id

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
                        street_name,
                        street_type_code,
                        street_suffix_code                      
                    FROM {dbschema}.street_locality_alias
                    WHERE street_locality_alias_pid = {id}''') \
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
                    street_name = row[1]
                    street_type = row[2].title()
                    street_suffix = row[3].title() if not row[3] == None else row[3]
                    street_string = '{} {} {}'\
                        .format(street_name, street_type, street_suffix)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_streetLocalityAlias_gnaf.html',
                street_locality_alias_id=self.id,
                street_name=street_name,
                street_type=street_type,
                street_suffix=street_suffix,
                street_string=street_string,
                street_locality_id=street_locality_pid
            )

        elif view == 'ISO19160':
            view_html = render_template(
                'class_streetLocalityAlias_ISO19160.html',
            )

        elif view == 'dct':
            s = sql.SQL('''SELECT 
                        street_locality_pid, 
                        street_name,
                        street_type_code,
                        street_suffix_code                      
                    FROM {dbschema}.street_locality_alias
                    WHERE street_locality_alias_pid = {id}''') \
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
                for row in cursor:
                    street_locality_pid = row[0]
                    street_name = row[1]
                    street_type = row[2].title()
                    street_suffix = row[3].title()
                    street_string = '{} {} {}'\
                        .format(street_name, street_type, street_suffix)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_streetLocalityAlias_dct.html',
                identifier=self.id,
                title='Street Locality Alias' + self.id,
                description=street_string,
                source='G-NAF, 2016',
                type='StreetLocalityAlias'
            )

        return render_template(
            'class_streetLocalityAlias.html',
            view_html=view_html,
            street_locality_alias_id=self.id,
            street_locality_alias_uri=self.uri,
        )

    def export_rdf(self, view='ISO19160', format='text/turtle'):
        g = Graph()
        a = URIRef(self.uri)

        if view == 'ISO19160':
            # get the components from the DB needed for ISO19160
            s = sql.SQL('''SELECT 
                        street_locality_pid, 
                        street_name,
                        street_type_code,
                        street_suffix_code                      
                    FROM {dbschema}.street_locality_alias
                    WHERE street_locality_alias_pid = {id}''') \
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
                for row in cursor:
                    street_locality_pid = row[0]
                    street_name = row[1]
                    street_type = row[2].title()
                    street_suffix = row[3].title()
                    ac_street_value = '{} {} {}'\
                        .format(street_name, street_type, street_suffix)
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            AddressComponentTypeUriBase = 'http://def.isotc211.org/iso19160/-1/2015/Address/code/AddressComponentType/'

            ISO = Namespace('http://def.isotc211.org/iso19160/-1/2015/Address#')
            g.bind('iso19160', ISO)

            g.add((a, RDF.type, ISO.Address))

            ac_street = BNode()
            g.add((ac_street, RDF.type, ISO.AddressComponent))
            g.add((ac_street, ISO.valueInformation, Literal(ac_street_value, datatype=XSD.string)))
            g.add((ac_street, ISO.type, URIRef(AddressComponentTypeUriBase + 'thoroughfareName')))
            g.add((a, ISO.addressComponent, ac_street))

        elif view == 'gnaf':
            pass

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))
