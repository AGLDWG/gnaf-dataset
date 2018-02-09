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
    """
    The Register of Addresses

    :return: HTTP Response
    """
    # lists the views and formats available for a Sample
    views_formats = classes_functions.get_classes_views_formats() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        requested_view = request.values.get('_view')
        requested_format = request.values.get('_format')
        if requested_format is None:
            requested_format = request.accept_mimetypes.best_match(
                ['text/turtle', 'application/rdf+json', 'application/rdf+xml', 'text/html']
            )
        view, mime_format = LDAPI.get_valid_view_and_format(
            requested_view,
            requested_format,
            views_formats
        )
        # if alternates model, return this info from file
        class_uri = 'http://reference.data.gov.au/def/ont/iso19160-1-address#Address'

        if view == 'alternates':
            del views_formats['renderer']
            return render_alternates_view(
                class_uri,
                uparse.quote_plus(class_uri),
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
            links.append('<{}?per_page={}>; rel="first"'.format(config.URI_ADDRESS_INSTANCE_BASE, per_page))

            # if this is the first page, don't ad a prev link
            if page == 1:
                prev_page = 0
            else:
                prev_page = page - 1
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    config.URI_ADDRESS_INSTANCE_BASE,
                    per_page,
                    prev_page
                ))

            # add a link to "next" and "last"
            try:
                no_of_addresses = 14000000  # TODO: remove this outrageous magic number
                last_page = int(round(no_of_addresses / per_page, 0)) + 1  # same as math.ceil()

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
                                 .format(config.URI_ADDRESS_INSTANCE_BASE, per_page, (page + 1)))
                else:
                    next_page = None

                # add a link to "last"
                links.append('<{}?per_page={}&page={}>; rel="last"'
                             .format(config.URI_ADDRESS_INSTANCE_BASE, per_page, last_page))
            except Exception as e:
                print(e)
                # if there's some error in getting the no of samples, add the "next" link but not the "last" link
                next_page = page + 1
                links.append('<{}?per_page={}&page={}>; rel="next"'
                             .format(config.URI_ADDRESS_INSTANCE_BASE, per_page, (page + 1)))

            headers = {
                'Link': ', '.join(links)
            }

            return register.RegisterRenderer(
                request,
                config.URI_ADDRESS_INSTANCE_BASE,
                class_uri,
                None,
                page,
                per_page,
                prev_page,
                next_page,
                last_page).render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/addressSite/')
def address_sites():
    """
    Register of all address sites

    :return: LDAPI views of the Address Site register
    """
    # lists the views and mimetypes available for an Address Site Register (a generic Register)
    views_formats = LDAPI.get_classes_views_formats() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        class_uri = 'http://purl.org/linked-data/registry#Register'

        if view == 'alternates':
            del views_formats['renderer']
            return render_alternates_view(
                class_uri,
                uparse.quote_plus(class_uri),
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

            if per_page > 100:
                return Response(
                    'You must enter either no value for per_page or an integer <= 100.',
                    status=400,
                    mimetype='text/plain'
                )

            links = []
            links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
            links.append(
                '<http://www.w3.org/ns/ldp#Page>; rel="type"')  # signalling that this is, in fact, a resource described in pages
            links.append('<{}?per_page={}>; rel="first"'.format(config.URI_ADDRESS_SITE_INSTANCE_BASE, per_page))

            # if this isn't the first page, add a link to "prev"
            if page != 1:
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    config.URI_ADDRESS_SITE_INSTANCE_BASE,
                    per_page,
                    (page - 1)
                ))

            # add a link to "next" and "last"
            try:
                no_of_objects = 9200  # TODO replace this magic number
                last_page_no = int(round(no_of_objects / per_page, 0)) + 1  # same as math.ceil()

                # if we've gotten the last page value successfully, we can choke if someone enters a larger value
                if page > last_page_no:
                    return Response(
                        'You must enter either no value for page or an integer <= {} which is the last page number.'
                            .format(last_page_no),
                        status=400,
                        mimetype='text/plain'
                    )

                # add a link to "next"
                if page != last_page_no:
                    links.append(
                        '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_ADDRESS_SITE_INSTANCE_BASE, per_page, (page + 1)))

                # add a link to "last"
                links.append(
                    '<{}?per_page={}&page={}>; rel="last"'.format(config.URI_ADDRESS_SITE_INSTANCE_BASE, per_page, last_page_no))
            except:
                # if there's some error in getting the no of object, add the "next" link but not the "last" link
                links.append(
                    '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_ADDRESS_SITE_INSTANCE_BASE, per_page, (page + 1)))

            headers = {
                'Link': ', '.join(links)
            }

            return register.RegisterRenderer(request, class_uri, None, page, per_page, last_page_no) \
                .render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/streetLocality/')
def streets():
    """
    Register of all streets

    :return: LDAPI views of the Street register
    """
    # lists the views and mimetypes available for a Street Register (a generic Register)
    views_formats = LDAPI.get_classes_views_formats() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        class_uri = 'http://purl.org/linked-data/registry#Register'

        if view == 'alternates':
            del views_formats['renderer']
            return render_alternates_view(
                class_uri,
                uparse.quote_plus(class_uri),
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

            if per_page > 100:
                return Response(
                    'You must enter either no value for per_page or an integer <= 100.',
                    status=400,
                    mimetype='text/plain'
                )

            links = []
            links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
            links.append(
                '<http://www.w3.org/ns/ldp#Page>; rel="type"')  # signalling that this is, in fact, a resource described in pages
            links.append('<{}?per_page={}>; rel="first"'.format(config.URI_STREET_INSTANCE_BASE, per_page))

            # if this isn't the first page, add a link to "prev"
            if page != 1:
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    config.URI_STREET_INSTANCE_BASE,
                    per_page,
                    (page - 1)
                ))

            # add a link to "next" and "last"
            try:
                no_of_objects = 9200  # TODO replace this magic number
                last_page_no = int(round(no_of_objects / per_page, 0)) + 1  # same as math.ceil()

                # if we've gotten the last page value successfully, we can choke if someone enters a larger value
                if page > last_page_no:
                    return Response(
                        'You must enter either no value for page or an integer <= {} which is the last page number.'
                            .format(last_page_no),
                        status=400,
                        mimetype='text/plain'
                    )

                # add a link to "next"
                if page != last_page_no:
                    links.append(
                        '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_STREET_INSTANCE_BASE, per_page, (page + 1)))

                # add a link to "last"
                links.append(
                    '<{}?per_page={}&page={}>; rel="last"'.format(config.URI_STREET_INSTANCE_BASE, per_page, last_page_no))
            except:
                # if there's some error in getting the no of object, add the "next" link but not the "last" link
                links.append(
                    '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_STREET_INSTANCE_BASE, per_page, (page + 1)))

            headers = {
                'Link': ', '.join(links)
            }

            return register.RegisterRenderer(request, class_uri, None, page, per_page, last_page_no) \
                .render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/locality/')
def localities():
    """
    Register of all localities

    :return: LDAPI views of the Locality register
    """
    # lists the views and mimetypes available for a Locality Register (a generic Register)
    views_formats = LDAPI.get_classes_views_formats() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        view, mime_format = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        class_uri = 'http://purl.org/linked-data/registry#Register'

        if view == 'alternates':
            del views_formats['renderer']
            return render_alternates_view(
                class_uri,
                uparse.quote_plus(class_uri),
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

            if per_page > 100:
                return Response(
                    'You must enter either no value for per_page or an integer <= 100.',
                    status=400,
                    mimetype='text/plain'
                )

            links = []
            links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
            links.append(
                '<http://www.w3.org/ns/ldp#Page>; rel="type"')  # signalling that this is, in fact, a resource described in pages
            links.append('<{}?per_page={}>; rel="first"'.format(config.URI_LOCALITY_INSTANCE_BASE, per_page))

            # if this isn't the first page, add a link to "prev"
            if page != 1:
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    config.URI_LOCALITY_INSTANCE_BASE,
                    per_page,
                    (page - 1)
                ))

            # add a link to "next" and "last"
            try:
                no_of_objects = 9200  # TODO replace this magic number
                last_page_no = int(round(no_of_objects / per_page, 0)) + 1  # same as math.ceil()

                # if we've gotten the last page value successfully, we can choke if someone enters a larger value
                if page > last_page_no:
                    return Response(
                        'You must enter either no value for page or an integer <= {} which is the last page number.'
                            .format(last_page_no),
                        status=400,
                        mimetype='text/plain'
                    )

                # add a link to "next"
                if page != last_page_no:
                    links.append(
                        '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_LOCALITY_INSTANCE_BASE, per_page, (page + 1)))

                # add a link to "last"
                links.append(
                    '<{}?per_page={}&page={}>; rel="last"'.format(config.URI_LOCALITY_INSTANCE_BASE, per_page, last_page_no))
            except:
                # if there's some error in getting the no of object, add the "next" link but not the "last" link
                links.append(
                    '<{}?per_page={}&page={}>; rel="next"'.format(config.URI_LOCALITY_INSTANCE_BASE, per_page, (page + 1)))

            headers = {
                'Link': ', '.join(links)
            }

            return register.RegisterRenderer(request, class_uri, None, page, per_page, last_page_no) \
                .render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return client_error_Response(e)


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
        requested_view = request.values.get('_view')
        requested_format = request.values.get('_format')
        best_mime_match = request.accept_mimetypes.best_match(
                ['text/turtle', 'application/rdf+json', 'application/rdf+xml', 'text/html']
        )
        if best_mime_match != requested_format:
            requested_format = best_mime_match

        view, mimetype = LDAPI.get_valid_view_and_format(
            requested_view,
            requested_format,
            views_formats
        )

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
                return s.render(view, mimetype)
            except ValueError:
                return render_template('address_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/addressSite/<string:address_site_id>')
def address_site(address_site_id):
    """
    A single Address Site

    :param address_site_id:
    :return: LDAPI views of a single Address Site
    """
    # lists the views and formats available for class type C
    c = config.URI_ADDRESS_SITE_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mimetype = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

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
                return s.render(view, mimetype)
            except ValueError:
                return render_template('addressSite_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)


@classes.route('/streetLocality/<string:street_id>')
def street_locality(street_id):
    """
    A single street

    :param street_id:
    :return: LDAPI views of a single Street Locality
    """
    # lists the views and formats available for class type C
    c = config.URI_STREET_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mimetype = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_STREET_INSTANCE_BASE + street_id
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
                s = StreetRenderer(street_id)
                return s.render(view, mimetype)
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
    # lists the views and formats available for class type C
    c = config.URI_LOCALITY_CLASS
    views_formats = LDAPI.get_classes_views_formats().get(c)

    try:
        view, mimetype = LDAPI.get_valid_view_and_format(
            request.args.get('_view'),
            request.args.get('_format'),
            views_formats
        )

        # if alternates model, return this info from file
        if view == 'alternates':
            instance_uri = config.URI_LOCALITY_INSTANCE_BASE + locality_id
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
            from model.locality import LocalityRenderer
            try:
                s = LocalityRenderer(locality_id)
                return s.render(view, mimetype)
            except ValueError:
                return render_template('locality_no_record.html')

    except LdapiParameterError as e:
        return client_error_Response(e)

