from typing import List

from pytos.db.base import Database
from pytos.models.album import Album


class DatabaseAlbum:
    def __init__(self, db: Database):
        self.db = db

    def init(self):
        query = ('CREATE TABLE IF NOT EXISTS album('
                 '    id TEXT PRIMARY KEY,'
                 '    title TEXT,'
                 '    product_url TEXT,'
                 '    media_items_count TEXT,'
                 '    raw TEXT NOT NULL'
                 ')')
        self.db.execute(query)

    def add(self, item: Album, cursor=None, commit=True):
        query = 'INSERT OR REPLACE INTO album VALUES(:id, :title, :product_url, :media_items_count, :raw)'
        data = {
            'id': item.id,
            'title': item.title,
            'product_url': item.product_url,
            'media_items_count': item.media_items_count,
            'raw': item.raw
        }
        self.db.execute(query, data, cursor, commit)

    def add_multiple(self, data: List[Album]):
        cursor = self.db.conn.cursor()
        for item in data:
            self.add(item, cursor, False)
        self.db.conn.commit()
