import json


class Album:
    def __init__(self, _id, title, product_url, media_items_count, raw):
        self.id = _id
        self.title = title
        self.product_url = product_url
        self.media_items_count = media_items_count
        self.raw = raw

    @classmethod
    def from_dict(cls, js):
        _id = js['id']
        title = js['title']
        product_url = js['productUrl']
        media_items_count = int(js['mediaItemsCount'])
        raw = json.dumps(js)

        return Album(_id, title, product_url, media_items_count, raw)
