from typing import List

from pytos.db.base import Database
from pytos.models.media_item import MediaItem


class DatabaseMediaItem:
    def __init__(self, db: Database):
        self.db = db

    def init(self):
        query = ('CREATE TABLE IF NOT EXISTS media_item('
                 '    id TEXT PRIMARY KEY,'
                 '    base_url TEXT,'
                 '    product_url TEXT,'
                 '    mime_type TEXT,'
                 '    media_meta_data TEXT,'
                 '    filename TEXT,'
                 '    raw TEXT NOT NULL);')
        self.db.execute(query)

    def add(self, item: MediaItem, cursor=None, commit=True):
        query = ('INSERT OR REPLACE INTO media_item'
                 '  VALUES (:id, :base_url, :product_url, :mime_type, :media_meta_data, :filename, :raw)')
        data = {
            'id': item.id,
            'base_url': item.base_url,
            'product_url': item.product_url,
            'mime_type': item.mime_type,
            'media_meta_data': item.media_meta_data,
            'filename': item.filename,
            'raw': item.raw
        }
        self.db.execute(query, data, cursor, commit)

    def add_multiple(self, data: List[MediaItem]):
        cursor = self.db.conn.cursor()
        for item in data:
            self.add(item, cursor, False)
        self.db.conn.commit()
