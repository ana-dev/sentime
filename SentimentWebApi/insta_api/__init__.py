import requests
import time

from InstagramAPI import InstagramAPI

insta = InstagramAPI('', '') # confidential info deleted
try:
    insta.login()
    success = True
except Exception:
    success = False


def get_all_comments(url, count=5000):
    media_id = get_media_id(url)

    has_more_comments = True
    max_id = ''
    comments = []

    while has_more_comments:
        _ = insta.getMediaComments(media_id, max_id=max_id)

        # comments' page come from older to newer, lets preserve desc order in full list
        for c in reversed(insta.LastJson['comments']):
            comments.append(c)

        has_more_comments = insta.LastJson.get('has_more_comments', False)

        # evaluate stop conditions
        if count and len(comments) >= count:
            comments = comments[:count]
            # stop loop
            has_more_comments = False

        # next page
        if has_more_comments:
            max_id = insta.LastJson.get('next_max_id', '')
            time.sleep(2)

    return comments


def get_media_id(url):
    req = requests.get('https://api.instagram.com/oembed/?url={}'.format(url))
    media_id = req.json()['media_id']
    return media_id
