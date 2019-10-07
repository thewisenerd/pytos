from typing import Dict, List

from google.auth.credentials import Credentials

from pytos.models.album import Album
from pytos.models.album_item import AlbumItem
from pytos.models.context import Context
from pytos.models.rc import RunCommand
from pytos.oauth.base import Authorizer
from pytos.requests.album import get_all_albums
from pytos.requests.media_item import get_all_media_items
from pytos.requests.search import search_by_album_id


def fetch_album_items(credentials: Credentials, albums: Dict[str, Album]) -> List[AlbumItem]:
    wb = []
    for album_id in albums:
        wb.extend(search_by_album_id(credentials, album_id))
    return wb


class InitializeLibrary(RunCommand):
    def parse_args(self, args):
        return 0

    def run(self, context: Context):
        authorizer = Authorizer(context.cfg)
        credentials = authorizer.auth()
        context.cfg.refresh_token = credentials.refresh_token
        context.cfg.dump()

        media_items = get_all_media_items(credentials)
        albums = get_all_albums(credentials)

        context.db.init_tables()
        context.db.media_item.add_multiple(media_items.values())
        context.db.album.add_multiple(albums.values())

        album_items = fetch_album_items(credentials, albums)
        context.db.album_item.add_multiple(album_items)
