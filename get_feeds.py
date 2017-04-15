""" A simple example script to get all posts inside groups
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utility import Dedup, accessToken, storeDSN
from model.data import Group, Feed, Comment
from api import GraphAPI

logging.basicConfig(filename='example.log', level=logging.INFO)


def get_feed(graph, group_id, args=None):
    feeds = graph.request('{}/feed'.format(group_id), args)
    ret_feeds = []
    for key in feeds.keys():
        feed = feeds[key]
        if 'message' not in feed:
            continue # skip story-related feed
        f = Feed()
        f.id = feed['id']
        f.message = feed['message']
        f.updated_time = feed['updated_time']
        ret_feeds.append(f)
    return ret_feeds

def get_comment(graph, feed_id, args=None):
    comments = graph.request('{}/comments'.format(feed_id), args)
    ret_comments = []
    for key in comments.keys():
        comment = comments[key]
        c = Comment()
        c.id = comment['id']
        c.feed_id = feed_id
        c.from_id = comment['from']['id']
        c.message = comment['message']
        c.created_time = comment['created_time']
        ret_comments.append(c)
    return ret_comments

def run(session, onNewFeed=None, onNewComment=None):
    groupIds = ['575953955944382']

    graph = GraphAPI(accessToken(), logging=logging)
    for gid in groupIds:
        # get all feeds
        feeds = get_feed(graph, gid, {})
        for feed in feeds:
            if not feed.id:
                continue
            comments= get_comment(graph, feed.id, {})
            # write feed if it does not exist
            if not session.query(Feed).filter_by(id=feed.id).scalar():
                if onNewFeed: # hooks for new feed
                    onNewFeed(feed)
                session.add(feed)
            for comment in comments:
                if session.query(Comment).filter_by(id=comment.id).scalar():
                    continue
                if onNewComment: # hook for new comment
                    onNewComment(comment)
                session.add(comment)
    session.commit()


def main():
    engine = create_engine(storeDSN(), echo=False)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    def onNewComment(comment):
        print(comment)

    run(session, onNewComment=onNewComment)
    #dump(session)

    connection.close()

if __name__ == '__main__':
    main()
