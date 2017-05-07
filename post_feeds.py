#-*- coding: utf-8 -*-
"""
A simple example script to post a feed to a group on facebook.
"""

from utility import accessToken

from api import GraphAPI

import json

def post_feed(graph, post_args):
    """ post_feed post a feed with argument specified
    and return an id """

    # reference: https://developers.facebook.com/docs/graph-api/photo-uploads
    attached_medias = []
    for img in post_args['photos']:
        fbid = None
        caption = ''
        if 'caption' in img:
            caption = img['caption']

        if 'file' in img and img['file'] != '':
            fbid = graph.put_photo(
                image=open(img['file'], 'rb'),
                album_path="me/photos",
                kwargs={'caption':caption, 'published':False},
            )
        elif 'url' in img and img['url'] != '':
            fbid = graph.put_photo(
                image=None,
                album_path="me/photos",
                kwargs={'caption':caption, 'published':False, 'url':img['url']},
            )
        if not fbid:
            continue

        # NOTE: example of attached media:
        # { 'media_fbid': 'string-id'}
        attached_medias.append({
            'media_fbid': fbid['id'],
        })

    # link all unpublished photos
    payload = {
        'message': post_args['message'],
    }

    # make it into form-submit format
    # attached_media[0] = '{"media_fbid": "someid"}'
    # attached_media[1] = '{"media_fbid": "someid"}'
    for id in range(0, len(attached_medias)):
        key = 'attached_media[{}]'.format(id)
        payload[key] = json.dumps(attached_medias[id]) # NOTE: we should use string instad of json object

    postid = graph.post_request("me/feed", payload)
    return postid

def run():

    graph = GraphAPI(accessToken())
    feed_id = post_feed(
        graph,
        {
            'message': 'hello world',
            'photos': [
                {
                    'caption': 'this is photo1 from local',
                    'file': '/shops/nicktshirt.jpg',
                },
                {
                    'caption': 'this is photo2 from local',
                    'file': '/shops/nike-shoes.jpg',
                }
            ]}
    )
    print("id:%s"%feed_id)

def main():
    run()

if __name__ == '__main__':
    main()
