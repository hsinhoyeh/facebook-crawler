"""
This utility for accessing Facebook Graph API
"""

import facebook
import logging

from time import sleep

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
            sleep(0.1) # avoid to hit rate limit per second
            self.logging.info("search, url:%s, args:%s, count:%d, resp:%s", url, args, len(resp['data']), resp)
            for entity in resp['data']:
                if 'id' not in entity:
                    self.logging.info('skip entity: %s', entity)
                    continue
                gid = entity['id']
                id_to_entity[gid] = entity
            if 'paging' in resp and 'cursors' in resp['paging'] and 'after' in resp['paging']['cursors']:
                args['after'] = resp['paging']['cursors']['after']
            else:
                break # if no paging
        return id_to_entity

