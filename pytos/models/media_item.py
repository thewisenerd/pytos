import json


class MediaItem:
    def __init__(self, _id, description, base_url, product_url, mime_type, media_meta_data, filename, raw):
        self.id = _id
        self.description = description
        self.base_url = base_url
        self.product_url = product_url
        self.filename = filename
        self.mime_type = mime_type
        self.media_meta_data = media_meta_data
        self.raw = raw

    @classmethod
    def from_dict(cls, js):
        _id = js['id']

        description = None
        if 'description' in js:
            description = js['description']

        base_url = js['baseUrl']
        product_url = js['productUrl']
        mime_type = js['mimeType']
        filename = js['filename']

        media_meta_data = None
        if 'mediaMetadata' in js:
            media_meta_data = json.dumps(js['mediaMetadata'])

        raw = json.dumps(js)

        return MediaItem(_id, description, base_url, product_url, mime_type, media_meta_data, filename, raw)
