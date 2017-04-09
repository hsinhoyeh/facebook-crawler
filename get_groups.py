#-*- coding: utf-8 -*-
"""
A simple example script to get groups under a certain keywords.
"""
import facebook
import requests
import logging
import os
import re
import csv

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from model.data import Group
from string import ascii_lowercase
from time import sleep

logging.basicConfig(filename='example.log',level=logging.INFO)

maximum = 100000

class Dedup:
    seen_ids = {}
    def add(self, id):
        if id in self.seen_ids:
            return False
        self.seen_ids[id]=True
        return True
    def len(self):
        return len(self.seen_ids)

dedup = Dedup()

def accessToken():
    if 'fbToken' in os.environ:
        return os.environ['fbToken']
    return ""

def storeDSN():
    if 'dsn' in os.environ:
        return os.environ['dsn']
    return ""

def get_groups(session):

    queryArgs = {
        'q': 'b', # TODO: change query
        'type': 'group',
    }

    # recover all seen ids from db
    for g in session.query(Group).all():
        dedup.add(g.__dict__['id'])

    print("visited %d before", dedup.len())

    graph = facebook.GraphAPI(accessToken())
    for c in ascii_lowercase:
        queryArgs['q'] = c
        print("args:", queryArgs)
        get_group_in_deeper(session, graph, queryArgs)

def get_group_in_deeper(session, graph, args=None):
    dargs = dict(args)
    groups = request_in_deeper(graph, 'search', dargs)

    for key, entity in groups.items():
        if not dedup.add(entity['id']):
            continue
        if not re.search(u'[\u4e00-\u9fff]', entity['name']):
            logging.info("skip due to no chinese word: %s", entity['name'])
            continue
        members = request_in_deeper(graph, '{}/members'.format(entity['id']), {'limit': 1000})
        entity['members'] = len(members)

        dataIn = Group()
        dataIn.id = entity['id']
        dataIn.name = entity['name'].encode('unicode_escape')
        dataIn.privacy = entity['privacy']
        dataIn.members = entity['members']

        if not session.query(Group).filter_by(id=entity['id']).scalar():
            session.add(dataIn)
            session.commit()

""" return {'id': body:{}}} """
def request_in_deeper(graph, url, args=None):
    if 'limit' not in args:
        args['limit'] = 100
    id_to_info = {}
    while len(id_to_info) < maximum:
        resp = graph.request(url, args=args, method='GET')
        sleep(0.1) # avoid to hit rate limit per second
        logging.info("search, url:%s, args:%s, count:%d, resp:%s", url, args, len(resp['data']), resp)
        for group_entity in resp['data']:
            if 'id' not in group_entity:
                logging.info('skip group: %s', group_entity)
                continue
            gid = group_entity['id']
            id_to_info[gid] = group_entity
        if 'paging' in resp and 'cursors' in resp['paging'] and 'after' in resp['paging']['cursors']:
            args['after'] = resp['paging']['cursors']['after']
        else:
            break # if no paging
    return id_to_info

def dump(session):
    with open('example.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for group in session.query(Group).all():
            entity = group.__dict__
            name = entity['name'].encode('utf-8').decode('unicode_escape').replace('\n', '').replace(' ', '-').replace('，', '-').replace('、', '-')
            writer.writerow([str(entity['id']), name, entity['privacy'], entity['members']])

def run(session):
    get_groups(session)

def main():
    engine = create_engine(storeDSN(), echo=False)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    run(session)
    #dump(session)

    connection.close()

if __name__ == '__main__':
    main()
