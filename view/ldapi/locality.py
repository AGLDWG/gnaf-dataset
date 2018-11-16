# -*- coding: utf-8 -*-
from model.locality import Locality
from view.ldapi import GNAFClassRenderer
import _config as config


class LocalityRenderer(GNAFClassRenderer):
    GNAF_CLASS = config.URI_LOCALITY_CLASS

    def __init__(self, request, identifier, views, default_view_token, *args, **kwargs):
        _views = views or {}
        _uri = ''.join([config.URI_LOCALITY_INSTANCE_BASE, identifier])
        kwargs.setdefault('gnaf_template', 'class_locality.html')
        kwargs.setdefault('dct_template', 'class_locality.html')
        super(LocalityRenderer, self).__init__(request, _uri, _views, default_view_token, *args, **kwargs)
        self.identifier = identifier
        if self.view == 'alternates':
            self.instance = None
        else:
            self.instance = Locality(self.identifier)

    def _render_dct_view_xml(self):
        raise NotImplementedError("DCT XML view of Locality is not yet implemented.")

    def _render_gnaf_view_xml(self):
        raise NotImplementedError("GNAF XML view of Locality is not yet implemented.")

