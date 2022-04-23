"""
Aplicações Distribuídas - Projeto 3 - server/spotify.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""
from typing import Dict
from dotenv import load_dotenv
from os import getenv
from api import Api

load_dotenv()


class Spotify:
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

    def artist(self, artist_id: str):
        return self.api.get(f'/artists/{artist_id}', headers=self.headers())

    def track(self, track_id: str):
        return self.api.get(f'/tracks/{track_id}', headers=self.headers())
