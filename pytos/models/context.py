from pytos.db.album import DatabaseAlbum
from pytos.db.album_item import DatabaseAlbumItem
from pytos.db.base import Database
from pytos.db.media_item import DatabaseMediaItem
from pytos.models.configuration import Configuration


class DatabaseContext:
    def __init__(self, database: Database):
        self.media_item = DatabaseMediaItem(database)
        self.album = DatabaseAlbum(database)
        self.album_item = DatabaseAlbumItem(database)

    def init_tables(self):
        self.media_item.init()
        self.album.init()
        self.album_item.init()


class Context:
    def __init__(self, configuration: Configuration, database: Database):
        self.cfg = configuration
        self.db = DatabaseContext(database)
