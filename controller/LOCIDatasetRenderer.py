import pyldapi
import os
from flask import Response, render_template
from rdflib import Graph
import _config as config


class LOCIDatasetRenderer(pyldapi.RegisterOfRegistersRenderer):
    """
    Specialised implementation of the Renderer for displaying DCAT v2, VOID & Reg properties for the GNAF dataset as a
    whole. All content is contained in static HTML & RDT (turtle) files
    """
    def __init__(self, request, url=None, view=None, format=None):

        views = {
            'dcat': pyldapi.View(
                'Dataset Catalog Vocabulary - DCAT',
                'The DCAT view, according to DCATv2 (2018)',
                ['text/html'] + pyldapi.Renderer.RDF_MIMETYPES,
                'text/html',
                namespace='http://www.w3.org/ns/dcat'
            ),
            # 'reg': pyldapi.View(
            #     'Registry Ontology view',
            #     'A \'core ontology for registry services\': items are listed in Registers with acceptance statuses',
            #     ['text/html'] + pyldapi.Renderer.RDF_MIMETYPES,
            #     'text/html',
            #     namespace='http://purl.org/linked-data/registry'
            # ),
            'void': pyldapi.View(
                'Vocabulary of Interlinked Data Ontology view',
                'VoID is \'an RDF Schema vocabulary for expressing metadata about RDF datasets\'',
                pyldapi.Renderer.RDF_MIMETYPES,
                'text/turtle',
                namespace='http://rdfs.org/ns/void'
            ),
        }
        # push RofR properties up to the RofR constructor
        if url is None:
            url = request.url
        super().__init__(request, url, label="RofR", comment="RofR", rofr_file_path="./view/reg.ttl", views=views, default_view_token='dcat')

        # replace automatically-calculated view & format with specifically set ones
        if view is not None:
            self.view = view

        if format is not None:
            self.format = format

    def render(self):
        if self.view == 'alternates':
            return self._render_alternates_view()
            #
        elif self.view == 'reg':
            if self.format == "_internal":
                return self  # make the harvester work
            if self.format == 'text/html':
                return render_template('page_home_reg.html')
            else:
                return self._render_rdf_from_file('reg.ttl', self.format)
        elif self.view == 'void':
            # VoID view is only available in RDF
            return self._render_rdf_from_file('void.ttl', self.format)
        else:  # DCAT, default
            if self.format == 'text/html':
                return render_template('page_home.html')
            else:
                return self._render_rdf_from_file('dcat.ttl', self.format)

    def _render_rdf_from_file(self, file, format):
        if self.format == 'text/turtle':
            txt = open(os.path.join(config.APP_DIR, 'view', file), 'rb').read().decode('utf-8')
            return Response(txt, mimetype='text/turtle')
        else:
            g = Graph().parse(os.path.join(config.APP_DIR, 'view', file), format='turtle')
            if format == "_internal":
                return g
            return Response(
                g.serialize(destination=None, format=format, encoding='utf-8'),
                mimetype=format
            )

