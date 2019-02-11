#!/usr/bin/env python3

import os
import sys
import argparse
import statistics
import sqlite3

import toml

import google.auth.transport.requests
import google.oauth2.credentials

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession

parser = argparse.ArgumentParser()
parser.add_argument('CMD')

oauth_scopes = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata'
]

def validate_cfg(cfg):
    assert isinstance(cfg, dict)

    assert 'oauth' in cfg
    assert isinstance(cfg['oauth'], dict)

    assert 'secrets' in cfg['oauth']
    assert isinstance(cfg['oauth']['secrets'], str)

    assert os.path.exists(os.path.join('cfg', cfg['oauth']['secrets']))
    assert os.path.isfile(os.path.join('cfg', cfg['oauth']['secrets']))

    assert 'app' in cfg
    assert isinstance(cfg['app'], dict)

    assert 'db' in cfg['app']
    assert isinstance(cfg['app']['db'], str)

    if 'user' in cfg:
        assert isinstance(cfg['user'], dict)
        
        assert 'refresh_token' in cfg['user']
        assert isinstance(cfg['user']['refresh_token'], str)

def auth(cfg, scopes):
    secrets = os.path.join('cfg', cfg['oauth']['secrets'])

    flow = InstalledAppFlow.from_client_secrets_file(secrets,
                scopes=scopes,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    if 'user' in cfg:
        client_cfg = flow.client_config

        refresh_token = cfg['user']['refresh_token']
        refresh_req = google.auth.transport.requests.Request()

        fresh = google.oauth2.credentials.Credentials(None,
                    refresh_token=refresh_token, 
                    token_uri=client_cfg['token_uri'], 
                    client_id=client_cfg['client_id'], 
                    client_secret=client_cfg['client_secret'])
        fresh.refresh(refresh_req)

        if fresh.valid:
            return fresh

        print('refresh token expired. ', end='')

    credentials = flow.run_console(
                    authorization_prompt_message='please login:\n\n\t{url}\n',
                    authorization_code_message='auth code: ')
    return credentials

class Builder:
    def __init__(self, base, ver):
        self.__base = base
        self.__ver = ver

    def build(self, path):
        return 'https://{}/{}{}'.format(self.__base, self.__ver, path)

class MediaItem:
    def __init__(self, _id, desc, baseurl, mime, filename, meta=None):
        self.id = _id
        self.description = desc
        self.baseUrl = baseurl
        self.filename = filename
        self.mimeType = mime

        if meta is not None:
            self.meta = meta

    @classmethod
    def from_dict(cls, js):
        _id = js['id']

        desc = None
        if 'description' in js:
            desc = js['description']

        base = js['baseUrl']
        mime = js['mimeType']
        filename = js['filename']

        return MediaItem(_id, desc, base, mime, filename, js)

def init_library(credentials, conn):
    c = conn.cursor()

    cmd_init_table = '''
    CREATE TABLE IF NOT EXISTS mediaitems(
        id text PRIMARY KEY,
        baseUrl text,
        mimeType text,
        filename text
    );'''

    c.execute(cmd_init_table)
    conn.commit()

    cmd_select_rec = '''
    SELECT * from mediaitems where id = :id;
    '''

    cmd_insert_rec = '''
    INSERT OR REPLACE INTO mediaitems VALUES(:id, :baseUrl, :mimeType, :filename);
    '''

    a_session = AuthorizedSession(credentials)
    ub = Builder('photoslibrary.googleapis.com', 'v1')
    path = ub.build('/mediaItems')

    # dump all eg:
    url = path
    data = {'pageSize': 100}
    ctr = 0
    dup = 0
    latency = []
    ids = []
    while True:
        req = a_session.get(url, params=data)
        assert req.status_code == 200

        res = req.json()

        if 'mediaItems' not in res:
            break

        for _item in res['mediaItems']:
            item = MediaItem.from_dict(_item)

            # c.execute(cmd_select_rec, {'id': item.id})
            # existing = c.fetchall()
            # if len(existing) != 0:
            #     dup += 1
            #     # print('---')
            #     # print(existing[0][1])
            #     # print(item.baseUrl)
            #     # print('---')
            if item.id in ids:
                dup += 1
            else:
                ids.append(item.id)

            c.execute(cmd_insert_rec, {
                'id': item.id,
                'baseUrl': item.baseUrl,
                'mimeType': item.mimeType,
                'filename': item.filename,
            })

        print('{} {}'.format(len(res['mediaItems']), req.elapsed.total_seconds()))
        latency.append(req.elapsed.total_seconds())
        ctr += len(res['mediaItems'])
        data['pageToken'] = res['nextPageToken']

    conn.commit()
    conn.close()

    print('\n\ntotal:{}, dup:{} ({}), latency (avg): {}, (med): {}'.format(ctr, dup, (ctr - dup), statistics.mean(latency), statistics.median(latency)))

    return 0

def init_albums(credentials, conn):
    c = conn.cursor()

    cmd_init_table = '''
    CREATE TABLE IF NOT EXISTS albums(
        id text PRIMARY KEY,
        title text,
        mediaItemsCount text
    );
    '''

    c.execute(cmd_init_table)
    conn.commit()
    
    cmd_insert_rec = '''
    INSERT OR REPLACE INTO albums VALUES(:id, :title, :mediaItemsCount);
    '''

    a_session = AuthorizedSession(credentials)
    ub = Builder('photoslibrary.googleapis.com', 'v1')
    path = ub.build('/albums')

    # dump all albums:
    url = path
    data = {'pageSize': 50}
    ctr = 0
    latency = []
    while True:
        req = a_session.get(url, params=data)
        assert req.status_code == 200

        res = req.json()

        for it in res['albums']:
            _id = it['id']
            title = it['title']
            mediaItemsCount = it['mediaItemsCount']
            
            c.execute(cmd_insert_rec, {
                'id': _id,
                'title': title,
                'mediaItemsCount': mediaItemsCount,
            })

        print('{} {}'.format(len(res['albums']), req.elapsed.total_seconds()))
        latency.append(req.elapsed.total_seconds())
        ctr += len(res['albums'])

        if 'albums' not in res:
            break

        if 'nextPageToken' not in res:
            break

        data['pageToken'] = res['nextPageToken']

    conn.commit()
    conn.close()

    print('\n\ntotal:{}, latency (avg): {}, (med): {}'.format(ctr, statistics.mean(latency), statistics.median(latency)))

    return 0

def albums_meta(credentials, conn):
    c = conn.cursor()

    cmd_init_table = '''
    CREATE TABLE IF NOT EXISTS albums_meta(
        id text,
        album_id text
    );
    '''

    c.execute(cmd_init_table)
    conn.commit()

    cmd_get_albums = '''
    select * from albums;
    '''

    cmd_get_meta_id_album = '''
    select * from albums_meta where id = :id and album_id = :album_id;
    '''

    cmd_insert_meta_id_album = '''
    insert into albums_meta values(:id, :aid);
    '''

    a_session = AuthorizedSession(credentials)
    ub = Builder('photoslibrary.googleapis.com', 'v1')
    path = ub.build('/mediaItems:search')

    # dump all albums:
    url = path
    data = {'pageSize': 100}
    ctr = 0
    dup = 0
    latency = []

    c.execute(cmd_get_albums)
    albums = c.fetchall()

    for album in albums:
        aid = album[0]
        data.pop('pageToken', None)
        data['albumId'] = aid

        while True:
            # print(url, data)

            req = a_session.post(url, data=data)

            # print(req.status_code)
            assert req.status_code == 200

            res = req.json()

            if 'mediaItems' not in res:
                break


            for item in res['mediaItems']:
                c.execute(cmd_get_meta_id_album, {
                    'id': item['id'],
                    'album_id': aid,
                })

                existing = c.fetchall()
                if len(existing) != 0:
                    dup += 1
                    # continue
                else:
                    c.execute(cmd_insert_meta_id_album, {
                        'id': item['id'],
                        'aid': aid,
                    })
                    conn.commit()

            print('{} {}'.format(len(res['mediaItems']), req.elapsed.total_seconds()))
            latency.append(req.elapsed.total_seconds())
            ctr += len(res['mediaItems'])

            if 'nextPageToken' not in res:
                break

            data['pageToken'] = res['nextPageToken']

        conn.commit()
        print('\n\n{} :: total:{}, latency (avg): {}, (med): {}'.format(album[1], ctr, statistics.mean(latency), statistics.median(latency)))

    conn.close()

    return 0

def mediaitems_get(credentials, conn, _id):
    a_session = AuthorizedSession(credentials)
    ub = Builder('photoslibrary.googleapis.com', 'v1')
    path = ub.build('/mediaItems/{}'.format(_id))

    url = path
    req = a_session.get(url)
    assert req.status_code == 200

    res = req.json()

    print('{}'.format(res['mediaMetadata']['creationTime']))
    print('---')
    print('{}'.format(res['baseUrl']))

    conn.close()
    return 0

cmd_valid = ['init_library', 'init_albums', 'albums_meta']
cmd_startswith = ['get']
def check_cmd(cmd):

    if cmd in cmd_valid:
        return (cmd, None)

    for s in cmd_startswith:
        if cmd.startswith('{}:'.format(s)):
            return (cmd, cmd[len(s)+1:])

    return (None, None)

def main():
    pwd = os.getcwd()
    cfg_file = 'cfg/app.cfg'
    args = vars(parser.parse_args())

    (cmd, arg) = check_cmd(args['CMD'])
    if cmd == None:
        print('invalid command, try: {}'.format(', '.join(cmd_valid)))
        print('or: {}'.format(', '.join([s + ':ID' for s in cmd_startswith])))
        return 1

    if not os.path.exists(cfg_file):
        print('config file does not exist!')
        return 1

    # fix perms
    os.chmod(cfg_file, 0o600)

    cfg = toml.load(cfg_file)
    validate_cfg(cfg)

    credentials = auth(cfg, oauth_scopes)

    # refresh refresh token
    cfg['user'] = {
        'refresh_token': credentials.refresh_token
    }
    with open(cfg_file, 'w') as fp:
        toml.dump(cfg, fp)

    db_file = cfg['app']['db']
    conn = sqlite3.connect(db_file)

    if cmd == 'init_library':
        return init_library(credentials, conn)
    if cmd == 'init_albums':
        return init_albums(credentials, conn)
    if cmd == 'albums_meta':
        return albums_meta(credentials, conn)
    if cmd.startswith('get:'):
        return mediaitems_get(credentials, conn, arg)

    return 0

if __name__ == '__main__':
    sys.exit(main())
