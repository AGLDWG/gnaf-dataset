"""
This file contains all the HTTP routes for classes from the IGSN model, such as Samples and the Sample Register
"""
from flask import Blueprint, render_template, request, Response
from .functions import render_alternates_view, client_error_Response
import _config
from _ldapi.ldapi import LDAPI, LdapiParameterError
import urllib.parse as uparse

model_classes = Blueprint('model_classes', __name__)


@model_classes.route('/address/')
def addresses():
    """
    Register of all addresses

    :return: LDAPI views of the Address register
    """
    return 'Addresses'


@model_classes.route('/address/<string:address_id>')
def address(address_id):
    """
    A single Address

    :param address_id:
    :return: LDAPI views of a single Address
    """
    # lists the views and formats available for class type C
    c = 'http://reference.data.gov.au/def/ont/gnaf#Address'
    views_formats = LDAPI.get_classes_views_formats() \
        .get(c)

    try:
        view, mimetype = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = 'http://transport.data.gov.au/id/address/' + address_id
            del views_formats['renderer']
            return render_alternates_view(
                c,
                uparse.quote_plus(c),
                instance_uri,
                uparse.quote_plus(instance_uri),
                views_formats,
                request.args.get('_format')
            )
        else:
            from model.address import Address
            try:
                s = Address(address_id)
                return s.render(view, mimetype)
            except ValueError:
                return render_template('address_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)
