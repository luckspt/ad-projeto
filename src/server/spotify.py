from typing import Dict
from dotenv import load_dotenv
from os import getenv
from api import Api

load_dotenv()

class Spotify():
    api: Api = None

    def __init__(self) -> None:
        self.api = Api('https://api.spotify.com/v1')

    def get_token(self):
        return getenv('SPOTIFY_TOKEN')

    def headers(self) -> Dict[str, str]:
        headers = {
            'User-Agent': 'FCUL-LTI-AD Projeto3-G21',
            'Authorization': f'Bearer {self.get_token()}'
        }

        return headers

    def artist(self, id: str):
        return self.api.get(f'/artists/{id}', headers=self.headers())

    def track(self, id: str):
        return self.api.get(f'/tracks/{id}', headers=self.headers())
