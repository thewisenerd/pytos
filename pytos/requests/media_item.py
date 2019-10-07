from typing import Dict

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

from pytos.models.media_item import MediaItem
from pytos.requests.builder import Builder
from pytos.requests.context import RequestContext


def get_all_media_items(credentials: Credentials) -> Dict[str, MediaItem]:
    a_session = AuthorizedSession(credentials)
    ub = Builder('photoslibrary.googleapis.com', 'v1')
    url = ub.build('/mediaItems')

    # dump all eg:
    params = {'pageSize': 100}
    wb = {}
    context = RequestContext('get_all_media_items')
    while True:
        req = a_session.get(url, params=params)
        assert req.status_code == 200
        res = req.json()

        if 'mediaItems' not in res:
            break

        dup = 0
        for _item in res['mediaItems']:
            item = MediaItem.from_dict(_item)
            if item.id in wb:
                dup += 1
            wb[item.id] = item

        context.add(req.elapsed.total_seconds(), len(res['mediaItems']), dup)

        if 'nextPageToken' not in res:
            break

        params['pageToken'] = res['nextPageToken']

    context.stat()

    return wb
