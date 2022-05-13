"""
Aplicações Distribuídas - Projeto 4 - server/spotify.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""
from typing import Any, Dict, Union
import requests
from requests_oauthlib import OAuth2Session
from exceptions import ApiException

SPOTIFY_BASE_URL = 'https://api.spotify.com/v1'
SPOTIFY_ACCOUNTS_BASE_URL = 'https://accounts.spotify.com'


def parse_response(res: requests.Response) -> Union[Dict[str, Any], None]:
    try:
        json = res.json()
        if res.status_code >= 200 and res.status_code < 300:
            return json
        else:
            raise ApiException(
                'API Error', json['error']['message'], res.status_code)
    except ValueError:
        return None


class Spotify:
    client_secret: str = None
    api: OAuth2Session = None

    def __init__(self, client_id: str, client_secret: str, oauth_redirect: str = 'https://localhost:5000/callback') -> None:
        self.api = OAuth2Session(client_id, redirect_uri=oauth_redirect)
        self.client_secret = client_secret

    def authorize(self) -> str:
        auth_url, _ = self.api.authorization_url(
            f'{SPOTIFY_ACCOUNTS_BASE_URL}/authorize')
        return auth_url

    def fetch_token(self, url: str) -> None:
        return self.api.fetch_token(f'{SPOTIFY_ACCOUNTS_BASE_URL}/api/token',
                                    client_secret=self.client_secret, authorization_response=url)

    def me(self):
        return parse_response(self.api.get(f'{SPOTIFY_BASE_URL}/me'))

    def artist(self, artist_id: str):
        return parse_response(self.api.get(f'{SPOTIFY_BASE_URL}/artists/{artist_id}'))

    def track(self, track_id: str):
        return parse_response(self.api.get(f'{SPOTIFY_BASE_URL}/tracks/{track_id}'))
