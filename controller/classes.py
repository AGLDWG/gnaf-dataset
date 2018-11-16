# -*- coding: utf-8 -*-
"""
This file contains all the HTTP routes for classes from the GNAF model, such as Address and the Address Register
"""
from flask import Blueprint, request
import _config as config
from view.ldapi import GNAFRegisterRenderer
from view.ldapi.address import AddressRenderer
from view.ldapi.addressSite import AddressSiteRenderer
from view.ldapi.locality import LocalityRenderer
from view.ldapi.streetLocality import StreetLocalityRenderer


classes = Blueprint('classes', __name__)


@classes.route('/address/')
def addresses():
    renderer = GNAFRegisterRenderer(request, config.URI_ADDRESS_INSTANCE_BASE,
                                    "Address Register",
                                    "Register of all GNAF Addresses",
                                    [config.URI_ADDRESS_CLASS],
                                    config.ADDRESS_COUNT,
                                    super_register=config.URI_BASE)
    return renderer.render()


# noinspection PyPep8Naming
@classes.route('/addressSite/')
def addressSites():
    renderer = GNAFRegisterRenderer(request, config.URI_ADDRESS_SITE_INSTANCE_BASE,
                                    "Address Site Register",
                                    "Register of all GNAF Address Sites",
                                    [config.URI_ADDRESS_SITE_CLASS],
                                    config.ADDRESS_SITE_COUNT,
                                    super_register=config.URI_BASE)
    return renderer.render()


# noinspection PyPep8Naming
@classes.route('/streetLocality/')
def streetLocalities():
    renderer = GNAFRegisterRenderer(request, config.URI_STREETLOCALITY_INSTANCE_BASE,
                                    "Street Locality Register",
                                    "Register of all GNAF Street Localities",
                                    [config.URI_STREETLOCALITY_CLASS],
                                    config.STREET_LOCALITY_COUNT,
                                    super_register=config.URI_BASE)
    return renderer.render()


@classes.route('/locality/')
def localities():
    renderer = GNAFRegisterRenderer(request, config.URI_LOCALITY_INSTANCE_BASE,
                                    "Locality Register",
                                    "Register of all GNAF Localities",
                                    [config.URI_LOCALITY_CLASS],
                                    config.LOCALITY_COUNT,
                                    super_register=config.URI_BASE)
    return renderer.render()


@classes.route('/address/<string:address_id>')
def address(address_id):
    """
    A single Address

    :param address_id:
    :return: LDAPI views of a single Address
    """
    r = AddressRenderer(request, address_id, None, 'gnaf')
    return r.render()


# noinspection PyPep8Naming
@classes.route('/addressSite/<string:address_site_id>')
def addressSite(address_site_id):
    """
    A single Address Site

    :param address_site_id:
    :return: LDAPI views of a single Address Site
    """
    r = AddressSiteRenderer(request, address_site_id, None, 'gnaf')
    return r.render()


# noinspection PyPep8Naming
@classes.route('/streetLocality/<string:street_locality_id>')
def streetLocality(street_locality_id):
    """
    A single street

    :param street_locality_id:
    :return: LDAPI views of a single Street Locality
    """
    r = StreetLocalityRenderer(request, street_locality_id, None, 'gnaf')
    return r.render()


@classes.route('/locality/<string:locality_id>')
def locality(locality_id):
    """
    A single locality

    :param locality_id:
    :return: LDAPI views of a single Locality
    """
    r = LocalityRenderer(request, locality_id, None, 'gnaf')
    return r.render()
