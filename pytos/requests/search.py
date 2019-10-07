from typing import List

from google.auth.app_engine import Credentials
from google.auth.transport.requests import AuthorizedSession

from pytos.models.album_item import AlbumItem
from pytos.models.media_item import MediaItem
from pytos.requests.builder import Builder
from pytos.requests.context import RequestContext


def search(credentials: Credentials, search_id: str, query_params: dict) -> List[MediaItem]:
    a_session = AuthorizedSession(credentials)
    ub = Builder('photoslibrary.googleapis.com', 'v1')
    url = ub.build('/mediaItems:search')

    # dump all eg:
    params = {'pageSize': 100}
    for k in query_params:
        params[k] = query_params[k]
    wb = []
    context = RequestContext(search_id)
    while True:
        req = a_session.post(url, data=params)
        assert req.status_code == 200
        res = req.json()

        if 'mediaItems' not in res:
            break

        for _item in res['mediaItems']:
            wb.append(MediaItem.from_dict(_item))

        context.add(req.elapsed.total_seconds(), len(res['mediaItems']), 0)

        if 'nextPageToken' not in res:
            break

        params['pageToken'] = res['nextPageToken']

    context.stat()

    return wb


def search_by_album_id(credentials: Credentials, album_id: str) -> List[AlbumItem]:
    params = {
        'albumId': album_id
    }
    search_id = 'search.album_id:{}'.format(album_id)
    results = search(credentials, search_id, params)
    return [AlbumItem(album_id, x.id) for x in results]
