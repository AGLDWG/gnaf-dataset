from .renderer import Renderer
from flask import Response, render_template
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal
from _ldapi import LDAPI
import _config as config
import psycopg2
from psycopg2 import sql


class RegisterRenderer(Renderer):
    def __init__(self, request, uri, endpoints, page, per_page, last_page_no):
        Renderer.__init__(self, uri, endpoints)

        self.request = request
        self.uri = uri
        self.register = []
        self.g = None
        self.per_page = per_page
        self.page = page
        self.last_page_no = last_page_no

        self._get_data_from_db(page, per_page)

    def render(self, view, mimetype, extra_headers=None):
        if view == 'reg':
            # is an RDF format requested?
            if mimetype in LDAPI.get_rdf_mimetypes_list():
                # it is an RDF format so make the graph for serialization
                self._make_reg_graph(view)
                rdflib_format = LDAPI.get_rdf_parser_for_mimetype(mimetype)
                return Response(
                    self.g.serialize(format=rdflib_format),
                    status=200,
                    mimetype=mimetype,
                    headers=extra_headers
                )
            elif mimetype == 'text/html':
                return Response(
                    render_template(
                        'class_register.html',
                        class_name=self.uri,
                        register=self.register
                    ),
                    mimetype='text/html',
                    headers=extra_headers
                )
        else:
            return Response('The requested model model is not valid for this class', status=400, mimetype='text/plain')

    def _get_data_from_db(self, page, per_page):
        try:
            connect_str = "host='{}' dbname='{}' user='{}' password='{}'"\
                .format(
                    config.DB_HOST,
                    config.DB_DBNAME,
                    config.DB_USR,
                    config.DB_PWD
                )
            conn = psycopg2.connect(connect_str)
            cursor = conn.cursor()
            # get just IDs, ordered, from the address_detail table, paginated by class init args
            id_query = sql.SQL('''
                SELECT address_detail_pid
                FROM {dbschema}.address_detail
                ORDER BY address_detail_pid
                LIMIT {limit}
                OFFSET {offset}
                ''').format(dbschema=sql.Identifier(config.DB_SCHEMA), limit=sql.Literal(per_page), offset=sql.Literal((page - 1) * per_page))
            cursor.execute(id_query)
            rows = cursor.fetchall()
            for row in rows:
                self.register.append(row[0])
        except Exception as e:
            print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
            print(e)

    def _make_reg_graph(self, model_view):
        self.g = Graph()

        if model_view == 'reg':  # reg is default
            # make the static part of the graph
            REG = Namespace('http://purl.org/linked-data/registry#')
            self.g.bind('reg', REG)

            LDP = Namespace('http://www.w3.org/ns/ldp#')
            self.g.bind('ldp', LDP)

            XHV = Namespace('https://www.w3.org/1999/xhtml/vocab#')
            self.g.bind('xhv', XHV)

            register_uri = URIRef(self.request.base_url)
            self.g.add((register_uri, RDF.type, REG.Register))
            self.g.add((register_uri, RDFS.label, Literal('Address Register', datatype=XSD.string)))

            page_uri_str = self.request.base_url
            if self.per_page is not None:
                page_uri_str += '?per_page=' + str(self.per_page)
            else:
                page_uri_str += '?per_page=100'
            page_uri_str_no_page_no = page_uri_str + '&page='
            if self.page is not None:
                page_uri_str += '&page=' + str(self.page)
            else:
                page_uri_str += '&page=1'
            page_uri = URIRef(page_uri_str)

            # pagination
            # this page
            self.g.add((page_uri, RDF.type, LDP.Page))
            self.g.add((page_uri, LDP.pageOf, register_uri))

            # links to other pages
            self.g.add((page_uri, XHV.first, URIRef(page_uri_str_no_page_no + '1')))
            self.g.add((page_uri, XHV.last, URIRef(page_uri_str_no_page_no + str(self.last_page_no))))

            if self.page != 1:
                self.g.add((page_uri, XHV.prev, URIRef(page_uri_str_no_page_no + str(self.page - 1))))

            if self.page != self.last_page_no:
                self.g.add((page_uri, XHV.next, URIRef(page_uri_str_no_page_no + str(self.page + 1))))

            # add all the items
            for item in self.register:
                item_uri = URIRef(self.request.base_url + item)
                self.g.add((item_uri, RDF.type, URIRef(self.uri)))
                self.g.add((item_uri, RDFS.label, Literal('Address ID:' + item, datatype=XSD.string)))
                self.g.add((item_uri, REG.register, page_uri))
