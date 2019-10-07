import os

import toml


class Configuration:
    def __init__(self, path):
        self.path = path
        self.buf = toml.load(path)

    def validate(self) -> int:
        cfg = self.buf

        assert isinstance(cfg, dict)

        assert 'oauth' in cfg
        assert isinstance(cfg['oauth'], dict)

        assert 'secrets' in cfg['oauth']
        assert isinstance(cfg['oauth']['secrets'], str)

        if 'refresh_token' in cfg:
            assert isinstance(cfg['user']['refresh_token'], str)

        p1 = cfg['oauth']['secrets']
        p2 = os.path.join('cfg', cfg['oauth']['secrets'])
        assert (os.path.isfile(p1) or os.path.isfile(p2))

        assert 'app' in cfg
        assert isinstance(cfg['app'], dict)

        assert 'db' in cfg['app']
        assert isinstance(cfg['app']['db'], str)

        return 0

    def dump(self):
        with open(self.path, 'w') as fp:
            toml.dump(self.buf, fp)

    def get_db(self) -> str:
        cfg = self.buf
        return cfg['app']['db']

    db = property(get_db)

    def get_secrets(self) -> str:
        cfg = self.buf
        p1 = cfg['oauth']['secrets']
        p2 = os.path.join('cfg', cfg['oauth']['secrets'])
        return p1 if os.path.isfile(p1) else p2

    secrets = property(get_secrets)

    def get_refresh_token(self) -> str:
        cfg = self.buf
        return cfg['oauth']['refresh_token'] if 'refresh_token' in cfg['oauth'] else None

    def set_refresh_token(self, token):
        cfg = self.buf
        oauth = cfg['oauth']
        oauth['refresh_token'] = token
        cfg['oauth'] = oauth
        self.buf = cfg

    refresh_token = property(get_refresh_token, set_refresh_token)
