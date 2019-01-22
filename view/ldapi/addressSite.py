# -*- coding: utf-8 -*-
from model import NotFoundError
from model.addressSite import AddressSite
from view.ldapi import GNAFClassRenderer
import _config as config


class AddressSiteRenderer(GNAFClassRenderer):
    GNAF_CLASS = config.URI_ADDRESS_SITE_CLASS

    def __init__(self, request, identifier, views, default_view_token, *args, **kwargs):
        _views = views or {}
        _uri = ''.join([config.URI_ADDRESS_SITE_INSTANCE_BASE, identifier])
        kwargs.setdefault('gnaf_template', 'class_addressSite.html')
        kwargs.setdefault('dct_template', 'class_addressSite.html')
        super(AddressSiteRenderer, self).__init__(request, _uri, _views, default_view_token, *args, **kwargs)
        self.identifier = identifier
        if self.view == 'alternates':
            self.instance = None
        else:
            try:
                self.instance = AddressSite(self.identifier)
            except NotFoundError as nfe:
                self.instance = nfe

    def _render_dct_view_xml(self):
        raise NotImplementedError("DCT XML view of AddressSite is not yet implemented.")

    def _render_gnaf_view_xml(self):
        raise NotImplementedError("GNAF XML view of AddressSite is not yet implemented.")

