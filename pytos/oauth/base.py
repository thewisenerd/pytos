import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from pytos.models.configuration import Configuration

oauth_scopes = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata'
]


class Authorizer:
    def __init__(self, config: Configuration):
        self.config = config
        self.credentials = Credentials

    def auth(self, scopes=None) -> Credentials:
        if scopes is None:
            scopes = oauth_scopes

        flow = InstalledAppFlow.from_client_secrets_file(self.config.secrets,
                                                         scopes=scopes,
                                                         redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        refresh_token = self.config.refresh_token
        if refresh_token is not None:
            client_cfg = flow.client_config
            refresh_req = Request()

            fresh = Credentials(None,
                                refresh_token=refresh_token,
                                token_uri=client_cfg['token_uri'],
                                client_id=client_cfg['client_id'],
                                client_secret=client_cfg['client_secret'])
            fresh.refresh(refresh_req)
            if fresh.valid:
                return fresh

            print('cfg.user.refresh_token expired. ', end='', file=sys.stderr)

        credentials = flow.run_console(
            authorization_prompt_message='please login:\n\n\t{url}\n',
            authorization_code_message='auth code: ')
        return credentials
