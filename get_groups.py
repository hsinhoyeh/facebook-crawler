#-*- coding: utf-8 -*-
"""
A simple example script to get groups under a certain keywords.
"""
import re
import csv
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utility import Dedup, accessToken, storeDSN
from model.data import Group
from api import GraphAPI

logging.basicConfig(filename='example.log', level=logging.INFO)

dedup = Dedup()

def get_groups(session):

    queryArgs = {
        'q': 'b', # TODO: change query
        'type': 'group',
    }

    # recover all seen ids from db
    for g in session.query(Group).all():
        dedup.add(g.__dict__['id'])

    print("visited %d before", dedup.len())

    graph = GraphAPI(accessToken(), logging=logging)
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
    return graph.request(url, args)

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
