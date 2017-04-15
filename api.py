"""
This utility for accessing Facebook Graph API
"""

import facebook
import logging

import time
import pytz
import calendar
from datetime import datetime

MAXIMUM_ELEMENTS = 100000

class GraphAPI(object):
    def __init__(self, access_token=None, logging=None, options=None):
        self.access_token = access_token
        self.graph = facebook.GraphAPI(self.access_token)
        self.maximum_elemets = MAXIMUM_ELEMENTS
        if options and 'maximum_elements' in options:
            self.maximum_elemets = options['maximum_elemets']
        if not logging:
            self.logging = logging.basicConfig(filename='graphapi.log',level=logging.INFO)
        else:
            self.logging = logging


    def request(self, url, args=None):
        """Fetches the given path in the Graph API page by page.
        """
        if 'limit' not in args:
            args['limit'] = 100
        id_to_entity = {}
        while len(id_to_entity) < self.maximum_elemets:
            resp = self.graph.request(url, args=args, method='GET')
            time.sleep(0.1) # avoid to hit rate limit per second
            if 'data' not in resp:
                break # due to no data
            self.logging.info("search, url:%s, args:%s, count:%d, resp:%s", url, args, len(resp['data']), resp)
            for entity in resp['data']:
                if 'id' not in entity:
                    self.logging.info('skip entity: %s', entity)
                    continue
                gid = entity['id']
                # handle encoding and time related format
                id_to_entity[gid] = encode(entity)
            if 'paging' in resp and 'cursors' in resp['paging'] and 'after' in resp['paging']['cursors']:
                args['after'] = resp['paging']['cursors']['after']
            else:
                break # if no paging
        return id_to_entity

def encode(entity):
    """ encode fields into python native format """
    if 'name' in entity:
        entity['name'] = entity['name'].encode('unicode_escape')
    if 'message' in entity:
        entity['message'] = entity['message'].encode('unicode_escape')
    if 'updated_time' in entity:
        entity['updated_time'] = encode_time(entity['updated_time'])
    if 'created_time' in entity:
        entity['created_time'] = encode_time(entity['created_time'])
    return entity

def encode_time(timeStr):
    """ convert a specific datetime format into datetime object"""
    strtime = time.strptime(timeStr, '%Y-%m-%dT%H:%M:%S+0000')
    return datetime.fromtimestamp(calendar.timegm(strtime), tz=pytz.utc)
