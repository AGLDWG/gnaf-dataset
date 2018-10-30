# -*- coding: utf-8 -*-
from flask import render_template, Response
from psycopg2 import sql
import pyldapi

import _config as config

DCTView = pyldapi.View('dct',
                       "Dublin Core Terms from the Dublin Core Metadata Initiative",
                       ["text/html", "text/turtle", "application/rdf+xml", "application/ld+json", "application/xml"],
                       "text/html", namespace="http://purl.org/dc/terms/")
GNAFView = pyldapi.View('gnaf',
                        "G-NAF web page view. A simple human-readable, web page-only view, based on the data model of PSMA's G-NAF as of August, 2017",
                        ["text/html", "text/turtle", "application/rdf+xml", "application/ld+json", "application/xml"],
                        "text/html", namespace="http://reference.data.gov.au/def/ont/gnaf/")
ISOView = pyldapi.View('ISO19160',
                       "The OWL ontology view of the ISO 19160-1:2015 Address standard from the OGC's TC211 UML to OWL mapping: https://github.com/ISO-TC211/GOM/tree/master/isotc211_GOM_harmonizedOntology/19160-1/2015",
                       ["text/turtle", "application/rdf+xml", "application/ld+json"],
                        "text/turtle", namespace="http://reference.data.gov.au/def/ont/iso19160-1-address#")
SchemaOrgView = pyldapi.View('schemaorg',
                             "An initiative by Bing, Google and Yahoo! to create and support a common set of schemas for structured data markup on web pages. It is serialised in JSON-LD",
                             ["application/ld+json"], "application/ld+json", namespace="http://schema.org")


def render_error(request, e):
    try:
        import traceback
        traceback.print_tb(e.__traceback__)
    except Exception:
        pass
    if isinstance(e, pyldapi.ViewsFormatsException):
        error_type = 'Internal View Format Error'
        error_code = 406
        error_message = e.args[0] or "No message"
    elif isinstance(e, NotImplementedError):
        error_type = 'Not Implemented'
        error_code = 406
        error_message = e.args[0] or "No message"
    elif isinstance(e, RuntimeError):
        error_type = 'Server Error'
        error_code = 500
        error_message = e.args[0] or "No message"
    else:
        error_type = 'Unknown'
        error_code = 500
        error_message = "An Unknown Server Error Occurred."

    resp_text = '''<?xml version="1.0"?>
    <error>
      <errorType>{}</errorType>
      <errorCode>{}</errorCode>
      <errorMessage>{}</errorMessage>
    </error>
    '''.format(error_type, error_code, error_message)
    return Response(resp_text, status=error_code, mimetype='application/xml')


class GNAFClassRenderer(pyldapi.Renderer):
    GNAF_CLASS = None

    def __init__(self, request, uri, views, default_view_token, *args,
                 gnaf_template=None, dct_template=None, **kwargs):
        kwargs.setdefault('alternates_template', 'alternates.html')
        _views = views or {}
        self._add_default_gnaf_views(_views)
        super(GNAFClassRenderer, self).__init__(request, uri, _views, default_view_token, *args, **kwargs)
        try:
            vf_error = self.vf_error
            if vf_error:
                if not hasattr(self, 'view') or not self.view:
                    self.view = 'gnaf'
                if not hasattr(self, 'format') or not self.format:
                    self.format = 'text/html'
        except AttributeError:
            pass
        self.gnaf_template = gnaf_template
        self.dct_template = dct_template
        self.identifier = None  # inheriting classes will need to add the Identifier themselves.
        self.instance = None  # inheriting classes will need to add the Instance themselves.

    def render(self):
        try:
            if self.view == 'alternates':
                return self._render_alternates_view()
            elif self.view == 'gnaf':
                return self._render_gnaf_view()
            elif self.view == 'dct':
                return self._render_dct_view()
            else:
                fn = getattr(self, '_render_{}_view'.format(str(self.view).lower()), None)
                if fn:
                    return fn()
                else:
                    raise RuntimeError("No renderer for view '{}'.".format(self.view))
        except Exception as e:
            from flask import request
            return render_error(request, e)

    def _render_alternates_view_html(self):
        views_formats = {k: v for k, v in self.views.items()}
        views_formats['default'] = self.default_view_token
        return Response(
            render_template(
                self.alternates_template or 'alternates.html',
                class_uri=self.GNAF_CLASS,
                instance_uri=self.uri,
                default_view_token=self.default_view_token,
                views_formats=views_formats
            ),
            headers=self.headers
        )

    def _render_gnaf_view(self):
        if self.format == 'text/html':
            return self._render_gnaf_view_html()
        elif self.format == 'application/xml':
            return self._render_gnaf_view_xml()
        elif self.format in GNAFClassRenderer.RDF_MIMETYPES:
            return self._render_gnaf_view_rdf()
        else:
            raise RuntimeError("Cannot render 'gnaf' View with format '{}'.".format(self.format))

    def _render_gnaf_view_xml(self):
        raise NotImplementedError("GNAF XML view of this Class is not yet implemented.")

    def _render_gnaf_view_html(self):
        view_html = self.instance.export_html(view='gnaf')
        return Response(render_template(
            self.gnaf_template,
            view_html=view_html,
            instance_id=self.identifier,
            instance_uri=self.uri,
            ),
            headers=self.headers)

    def _render_gnaf_view_rdf(self):
        g = self.instance.export_rdf('gnaf')
        return self._make_rdf_response(g)

    def _render_dct_view(self):
        if self.format == 'text/html':
            return self._render_dct_view_html()
        elif self.format == 'application/xml':
            return self._render_dct_view_xml()
        elif self.format in GNAFClassRenderer.RDF_MIMETYPES:
            return self._render_dct_view_rdf()
        else:
            raise RuntimeError("Cannot render 'dct' View with format '{}'.".format(self.format))

    def _render_dct_view_xml(self):
        raise NotImplementedError("DCT XML view of this Class is not yet implemented.")

    def _render_dct_view_rdf(self):
        g = self.instance.export_rdf('dct')
        return self._make_rdf_response(g)

    def _render_dct_view_html(self):
        view_html = self.instance.export_html(view='dct')
        return Response(render_template(
            self.dct_template,
            view_html=view_html,
            instance_id=self.identifier,
            instance_uri=self.uri,
            ),
            headers=self.headers)

    @classmethod
    def _add_default_gnaf_views(cls, _views):
        if 'gnaf' in _views.keys():
            raise pyldapi.ViewsFormatsException(
                 'You must not manually add a view with token \'gnaf\' as this is auto-created.'
            )
        if 'dct' in _views.keys():
            raise pyldapi.ViewsFormatsException(
                'You must not manually add a view with token \'dct\' as this is auto-created.'
            )
        _views['dct'] = DCTView
        _views['gnaf'] = GNAFView


class GNAFRegisterRenderer(pyldapi.RegisterRenderer):
    def _get_contained_items_from_db(self, page, per_page):
        cic = self.contained_item_classes[0]
        try:
            cursor = config.get_db_cursor()
            if cic == 'http://linked.data.gov.au/def/gnaf#Address':
                id_query = sql.SQL('''SELECT address_detail_pid
                                   FROM gnaf.address_detail
                                   ORDER BY address_detail_pid
                                   LIMIT {limit}
                                   OFFSET {offset}''').format(
                    limit=sql.Literal(per_page),
                    offset=sql.Literal((page - 1) * per_page)
                )
                label_prefix = 'Address'
            elif cic == 'http://linked.data.gov.au/def/gnaf#Locality':
                id_query = sql.SQL('''SELECT locality_pid
                                   FROM gnaf.locality
                                   ORDER BY locality_pid
                                   LIMIT {limit}
                                   OFFSET {offset}''').format(
                    limit=sql.Literal(per_page),
                    offset=sql.Literal((page - 1) * per_page)
                )
                label_prefix = 'Locality'
            elif cic == 'http://linked.data.gov.au/def/gnaf#StreetLocality':
                id_query = sql.SQL('''SELECT street_locality_pid
                                   FROM gnaf.street_locality
                                   ORDER BY street_locality_pid
                                   LIMIT {limit}
                                   OFFSET {offset}''').format(
                    limit=sql.Literal(per_page),
                    offset=sql.Literal((page - 1) * per_page)
                )
                label_prefix = 'Street Locality'
            elif cic == 'http://linked.data.gov.au/def/gnaf#AddressSite':
                id_query = sql.SQL('''SELECT address_site_pid
                                   FROM gnaf.address_site
                                   ORDER BY address_site_pid
                                   LIMIT {limit}
                                   OFFSET {offset}''').format(
                    limit=sql.Literal(per_page),
                    offset=sql.Literal((page - 1) * per_page)
                )
                label_prefix = 'Address Site'
            else:
                raise RuntimeError("Cannot get DB objects for unknown contained item class.")

            cursor.execute(id_query)
            rows = cursor.fetchall()
            for row in rows:
                item_pid = row[0]
                uri = ''.join([self.uri, item_pid])
                label = ' '.join([label_prefix, 'ID:', item_pid])
                self.register_items.append((uri, label, item_pid))
        except Exception as e:
            print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
            print(e)

    def __init__(self, _request, uri, label, comment, contained_item_classes,
                 register_total_count, *args, views=None,
                 default_view_token=None, **kwargs):
        kwargs.setdefault('alternates_template', 'alternates.html')
        kwargs.setdefault('register_template', 'class_register.html')
        super(GNAFRegisterRenderer, self).__init__(
            _request, uri, label, comment, None, contained_item_classes,
            register_total_count, *args, views=views,
            default_view_token=default_view_token, **kwargs)
        try:
            vf_error = self.vf_error
            if vf_error:
                if not hasattr(self, 'view') or not self.view:
                    self.view = 'reg'
                if not hasattr(self, 'format') or not self.format:
                    self.format = 'text/html'
        except AttributeError:
            pass
        self._get_contained_items_from_db(self.page, self.per_page)

    def render(self):
        try:
            return super(GNAFRegisterRenderer, self).render()
        except Exception as e:
            from flask import request
            return render_error(request, e)

    def _render_alternates_view_html(self):
        views_formats = {k: v for k, v in self.views.items()}
        views_formats['default'] = self.default_view_token
        return Response(
            render_template(
                self.alternates_template or 'alternates.html',
                class_uri="http://purl.org/linked-data/registry#Register",
                instance_uri=None,
                default_view_token=self.default_view_token,
                views_formats=views_formats
            ),
            headers=self.headers
        )


class ISO19160RendererMixin(object):

    def __init__(self, request, uri, views, *args, **kwargs):
        assert issubclass(self.__class__, GNAFClassRenderer),\
            "This Renderer Mixin only works on a GNAFClassRenderer."
        assert views is not None, "A mixin must be initialised on a class with a pre-created views dict."
        self._add_iso19160_views(views)
        super(ISO19160RendererMixin, self).__init__(request, uri, views, *args, **kwargs)

    @classmethod
    def _add_iso19160_views(cls, _views):
        if 'ISO19160' in _views.keys():
            raise pyldapi.ViewsFormatsException(
                'You must not manually add a view with token \'ISO19160\' as this is auto-created.'
            )
        _views['ISO19160'] = ISOView

    def _render_iso19160_view(self):
        if self.format in GNAFClassRenderer.RDF_MIMETYPES:
            return self._render_iso19160_view_rdf()
        elif self.format == 'text/html':
            raise NotImplementedError("HTML view of ISO19160 is not implemented.")
        else:
            raise RuntimeError("Cannot render format {}".format(self.format))

    def _render_iso19160_view_rdf(self):
        g = self.instance.export_rdf(view='ISO19160')
        return GNAFClassRenderer._make_rdf_response(self, g)


class SchemaOrgRendererMixin(object):

    def __init__(self, request, uri, views, *args, **kwargs):
        assert issubclass(self.__class__, GNAFClassRenderer),\
            "This Renderer Mixin only works on a GNAFClassRenderer."
        assert views is not None, "A mixin must be initialised on a class with a pre-created views dict."
        self._add_schema_org_views(views)
        super(SchemaOrgRendererMixin, self).__init__(request, uri, views, *args, **kwargs)

    @classmethod
    def _add_schema_org_views(cls, _views):
        if 'schemaorg' in _views.keys():
            raise pyldapi.ViewsFormatsException(
                'You must not manually add a view with token \'schemaorg\' as this is auto-created.'
            )
        _views['schemaorg'] = SchemaOrgView

    def _render_schemaorg_view(self):
        if self.format in ['application/ld+json', 'application/json']:
            return self._render_schemaorg_view_rdf()
        elif self.format in GNAFClassRenderer.RDF_MIMETYPES:
            raise NotImplementedError("Schema.org view only supports JSON-LD serialisation.")
        elif self.format == 'text/html':
            raise NotImplementedError("HTML format of Schema.org View is not implemented.")
        else:
            raise RuntimeError("Cannot render format {}".format(self.format))

    def _render_schemaorg_view_rdf(self):
        json_string = self.instance.export_schemaorg()
        return Response(json_string, mimetype=self.format, headers=self.headers)
