# -*- coding: utf-8 -*-
from model.address import Address
from view.ldapi import GNAFClassRenderer, SchemaOrgRendererMixin, ISO19160RendererMixin
import _config as config


class AddressRenderer(SchemaOrgRendererMixin, ISO19160RendererMixin, GNAFClassRenderer):
    GNAF_CLASS = config.URI_ADDRESS_CLASS

    def __init__(self, request, identifier, views, default_view_token, *args, **kwargs):
        _views = views or {}
        _uri = ''.join([config.URI_ADDRESS_INSTANCE_BASE, identifier])
        kwargs.setdefault('gnaf_template', 'class_address.html')
        kwargs.setdefault('dct_template', 'class_address.html')
        super(AddressRenderer, self).__init__(request, _uri, _views, default_view_token, *args, **kwargs)
        self.identifier = identifier
        if self.view == 'alternates':
            self.instance = None
        else:
            self.instance = Address(self.identifier, focus=True)

    def _render_dct_view_xml(self):
        raise NotImplementedError("DCT XML view of Address is not yet implemented.")

    def _render_gnaf_view_xml(self):
        raise NotImplementedError("GNAF XML view of Address is not yet implemented.")

