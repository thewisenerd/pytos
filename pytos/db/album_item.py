from typing import List

from pytos.db.base import Database
from pytos.models.album_item import AlbumItem


class DatabaseAlbumItem:
    def __init__(self, db: Database):
        self.db = db

    def init(self):
        query = ('CREATE TABLE IF NOT EXISTS album_item('
                 '    album_id TEXT,'
                 '    media_item_id TEXT,'
                 '    PRIMARY KEY (album_id, media_item_id)'
                 ')')
        self.db.execute(query)

    def add(self, item: AlbumItem, cursor=None, commit=True):
        query = 'INSERT OR REPLACE INTO album_item VALUES(:album_id, :media_item_id)'
        data = {
            'album_id': item.album_id,
            'media_item_id': item.media_item_id
        }
        self.db.execute(query, data, cursor, commit)

    def add_multiple(self, data: List[AlbumItem]):
        cursor = self.db.conn.cursor()
        for item in data:
            self.add(item, cursor, False)
        self.db.conn.commit()
