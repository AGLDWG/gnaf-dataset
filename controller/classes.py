"""
This file contains all the HTTP routes for classes from the GNAF model, such as Address and the Address Register
"""
from flask import Blueprint, render_template, request, Response
from .functions import render_alternates_view, client_error_Response
import _config as config
from _ldapi import LDAPI, LdapiParameterError
import urllib.parse as uparse
from controller import classes_functions

classes = Blueprint('classes', __name__)


@classes.route('/address/')
def addresses():
    return register(config.URI_ADDRESS_CLASS, config.URI_ADDRESS_INSTANCE_BASE, 14500000)


@classes.route('/addressSite/')
def addressSites():
    return register(config.URI_ADDRESS_SITE_CLASS, config.URI_ADDRESS_SITE_INSTANCE_BASE, 14500000)


@classes.route('/streetLocality/')
def streetLocalities():
    return register(config.URI_STREETLOCALITY_CLASS, config.URI_STREETLOCALITY_INSTANCE_BASE, 185663)


@classes.route('/locality/')
def localities():
    return register(config.URI_LOCALITY_CLASS, config.URI_LOCALITY_INSTANCE_BASE, 4786)


@classes.route('/address/<string:address_id>')
def address(address_id):
    """
    A single Address

    :param address_id:
    :return: LDAPI views of a single Address
    """
    # lists the views and formats available for class type C
    c = config.URI_ADDRESS_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(request, views_formats)

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_ADDRESS_INSTANCE_BASE + address_id
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
            from model.address import AddressRenderer
            try:
                s = AddressRenderer(address_id, True)
                return s.render(view, mime_format)
            except ValueError:
                return render_template('address_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/addressSite/<string:address_site_id>')
def addressSite(address_site_id):
    """
    A single Address Site

    :param address_site_id:
    :return: LDAPI views of a single Address Site
    """
    # lists the views and formats available for class type C
    c = config.URI_ADDRESS_SITE_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(request, views_formats)

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_ADDRESS_SITE_INSTANCE_BASE + address_site_id
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
            from model.addressSite import AddressSiteRenderer
            try:
                s = AddressSiteRenderer(address_site_id)
                return s.render(view, mime_format)
            except ValueError:
                return render_template('addressSite_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/streetLocality/<string:street_locality_id>')
def streetLocality(street_locality_id):
    """
    A single street

    :param street_locality_id:
    :return: LDAPI views of a single Street Locality
    """
    # lists the views and formats available for class type C
    c = config.URI_STREETLOCALITY_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(request, views_formats)

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_STREET_INSTANCE_BASE + street_locality_id
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
            from model.streetLocality import StreetRenderer
            try:
                s = StreetRenderer(street_locality_id)
                return s.render(view, mime_format)
            except ValueError:
                return render_template('street_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/locality/<string:locality_id>')
def locality(locality_id):
    """
    A single locality

    :param locality_id:
    :return: LDAPI views of a single Locality
    """
    # lists the views and formats available for class type config.URI_LOCALITY_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(config.URI_LOCALITY_CLASS)

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(request, views_formats)

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_LOCALITY_INSTANCE_BASE + locality_id
            del views_formats['renderer']
            return render_alternates_view(
                config.URI_LOCALITY_CLASS,
                uparse.quote_plus(config.URI_LOCALITY_CLASS),
                instance_uri,
                uparse.quote_plus(instance_uri),
                views_formats,
                request.args.get('_format')
            )
        else:
            from model.locality import LocalityRenderer
            try:
                s = LocalityRenderer(locality_id)
                return s.render(view, mime_format)
            except ValueError:
                return render_template('locality_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)


def register(uri_class, uri_instance_base, max):
    """
    Register of all localities

    :return: LDAPI views of the Locality register
    """
    # lists the views and mimetypes available for a Locality Register (a generic Register)
    views_formats = LDAPI.get_classes_views_formats() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(request, views_formats)

        if view == 'alternates':
            del views_formats['renderer']
            return render_alternates_view(
                uri_class,
                None,
                None,
                None,
                views_formats,
                request.args.get('_format')
            )
        else:
            from model import register

            # pagination
            page = int(request.args.get('page')) if request.args.get('page') is not None else 1
            per_page = int(request.args.get('per_page')) if request.args.get('per_page') is not None else 100

            if per_page > config.PAGE_SIZE:
                return Response(
                    'You must enter either no value for per_page or an integer <= {}.'.format(config.PAGE_SIZE),
                    status=400,
                    mimetype='text/plain'
                )

            links = []
            links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
            # signalling that this is, in fact, a resource described in pages
            links.append('<http://www.w3.org/ns/ldp#Page>; rel="type"')
            links.append('<{}?per_page={}>; rel="first"'.format(uri_instance_base, per_page))

            # if this is the first page, don't ad a prev link
            if page == 1:
                prev_page = 0
            else:
                prev_page = page - 1
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    uri_instance_base,
                    per_page,
                    prev_page
                ))

            # add a link to "next" and "last"
            try:
                last_page = int(round(max / per_page, 0)) + 1  # same as math.ceil()

                # if we've gotten the last page value successfully, we can choke if someone enters a larger value
                if page > last_page:
                    return Response(
                        'You must enter either no value for page or an integer <= {} which is the last page number.'
                            .format(last_page),
                        status=400,
                        mimetype='text/plain'
                    )

                # if this is not the last page, add a link to "next"
                if page != last_page:
                    next_page = page + 1
                    links.append('<{}?per_page={}&page={}>; rel="next"'
                                 .format(uri_instance_base, per_page, (page + 1)))
                else:
                    next_page = None

                # add a link to "last"
                links.append('<{}?per_page={}&page={}>; rel="last"'
                             .format(uri_instance_base, per_page, last_page))
            except Exception as e:
                print(e)
                # if there's some error in getting the no of samples, add the "next" link but not the "last" link
                next_page = page + 1
                links.append('<{}?per_page={}&page={}>; rel="next"'
                             .format(uri_instance_base, per_page, (page + 1)))

            headers = {
                'Link': ', '.join(links)
            }

            return register.RegisterRenderer(
                request,
                uri_instance_base,
                uri_class,
                None,
                page,
                per_page,
                prev_page,
                next_page,
                last_page).render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return client_error_Response(e)