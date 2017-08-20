"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
from flask import Blueprint, Response, request, render_template
from _ldapi.ldapi import LDAPI, LdapiParameterError

pages = Blueprint('routes', __name__)


@pages.route('/')
def index():
    return render_template(
        'page_index.html'
    )


@pages.route('/api')
def api():
    return render_template(
        'page_api.html'
    )
