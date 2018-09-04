# -*- coding: utf-8 -*-
from model.streetLocality import StreetLocality
from model.ldapi import GNAFClassRenderer
import _config as config


class StreetLocalityRenderer(GNAFClassRenderer):
    GNAF_CLASS = config.URI_STREETLOCALITY_CLASS

    def __init__(self, request, identifier, views, default_view_token, *args, **kwargs):
        _views = views or {}
        _uri = ''.join([config.URI_STREETLOCALITY_INSTANCE_BASE, identifier])
        kwargs.setdefault('gnaf_template', 'class_streetLocality.html')
        kwargs.setdefault('dct_template', 'class_streetLocality.html')
        super(StreetLocalityRenderer, self).__init__(request, _uri, _views, default_view_token, *args, **kwargs)
        self.identifier = identifier
        self.instance = StreetLocality(self.identifier)

    def _render_dct_view_xml(self):
        raise NotImplementedError("DCT XML view of StreetLocality is not yet implemented.")

    def _render_gnaf_view_xml(self):
        raise NotImplementedError("GNAF XML view of StreetLocality is not yet implemented.")

