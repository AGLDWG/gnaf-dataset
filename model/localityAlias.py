from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import _config as config
from _ldapi import LDAPI
import psycopg2
from psycopg2 import sql


class LocalityAliasRenderer(Renderer):
    """
    This class represents an Locality Alias and methods in this class allow an Locality Alias to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, id):
        # TODO: why doesn't this super thing work?
        # super(LocalityAliasRenderer, self).__init__(id)
        self.id = id
        self.uri = config.URI_LOCALITY_ALIAS_INSTANCE_BASE + id

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
                        a.locality_pid, 
                        a."name",
                        b.locality_name                    
                    FROM {dbschema}.locality_alias a
                      INNER JOIN {dbschema}.locality_view b ON a.locality_pid = b.locality_pid
                    WHERE locality_alias_pid = {id}''') \
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
                    locality_pid = row[0]
                    locality_name = row[1].title()
                    principal_name = row[2].title()
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_localityAlias_gnaf.html',
                locality_alias_id=self.id,
                locality_name=locality_name,
                locality_id=locality_pid,
                principal_name=principal_name
            )

        elif view == 'ISO19160':
            view_html = render_template(
                'class_localityAlias_ISO19160.html',
            )

        elif view == 'dct':
            s = sql.SQL('''SELECT 
                        locality_pid, 
                        "name"                  
                    FROM {dbschema}.locality_alias
                    WHERE locality_alias_pid = {id}''') \
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
                    locality_pid = row[0]
                    locality_name = row[1].title()
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            view_html = render_template(
                'class_localityAlias_dct.html',
                identifier=self.id,
                title='Locality Alias' + self.id,
                description=locality_name,
                source='G-NAF, 2016',
                type='LocalityAlias'
            )

        return render_template(
            'class_localityAlias.html',
            view_html=view_html,
            locality_alias_id=self.id,
            locality_alias_uri=self.uri,
        )

    def export_rdf(self, view='ISO19160', format='text/turtle'):
        g = Graph()
        a = URIRef(self.uri)

        if view == 'ISO19160':
            # get the components from the DB needed for ISO19160
            s = sql.SQL('''SELECT 
                        locality_pid, 
                        "name"                     
                    FROM {dbschema}.locality_alias
                    WHERE locality_alias_pid = {id}''') \
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
                    locality_pid = row[0]
                    locality_name = row[1].title()
            except Exception as e:
                print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
                print(e)

            AddressComponentTypeUriBase = 'http://def.isotc211.org/iso19160/-1/2015/Address/code/AddressComponentType/'

            ISO = Namespace('http://def.isotc211.org/iso19160/-1/2015/Address#')
            g.bind('iso19160', ISO)

            g.add((a, RDF.type, ISO.Address))

            ac_localityAlias = BNode()
            g.add((ac_localityAlias, RDF.type, ISO.AddressComponent))
            g.add((ac_localityAlias, ISO.valueInformation, Literal(locality_name, datatype=XSD.string)))
            g.add((ac_localityAlias, ISO.type, URIRef(AddressComponentTypeUriBase + 'localityName')))
            g.add((a, ISO.addressComponent, ac_localityAlias))

        elif view == 'gnaf':
            pass

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(format))
