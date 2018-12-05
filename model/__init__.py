# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class NotFoundError(Exception):
    def __init__(self, *args):
        super(NotFoundError, self).__init__(*args)


class GNAFModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, graph, uri):
        """Every thing to be rendered must at least have a graph (its data) and a URI (its ID)"""
        self.g = graph
        self.uri = uri

    @classmethod
    def make_wkt_literal(cls, longitude, latitude):
        return '<http://www.opengis.net/def/crs/EPSG/0/4283> POINT({} {})'.format(
            longitude, latitude
        )

