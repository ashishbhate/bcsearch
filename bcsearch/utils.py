import requests

from .constants import PUSHBULLET_API_KEY


def pb_notify(title, body):

    return requests.post("https://api.pushbullet.com/v2/pushes",
                         data={"type": "note",
                               "title": title,
                               "body": body},
                         auth=(PUSHBULLET_API_KEY, ''))
