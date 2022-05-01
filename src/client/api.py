# symlink on src/server/api.py
"""
Aplicações Distribuídas - Projeto 3 - client/api.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

from typing import Any, Dict, Union
import requests


def parse_response(res: requests.Response) -> Union[Dict[str, Any], None]:
    try:
        return res.json()
    except requests.exceptions.JSONDecodeError as e:
        return None


class Api:
    base_url: str = None

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get(self, path: str, query_params: Dict[str, str] = None, headers: Dict[str, str] = None) -> Union[Dict[str, Any], None]:
        res = requests.get(f'{self.base_url}{path}', params=query_params, headers=headers)
        return parse_response(res)

    def post(self, path: str, body: Dict[str, str], headers: Dict[str, str] = None) -> Union[Dict[str, Any], None]:
        res = requests.post(f'{self.base_url}{path}', json=body, headers=headers)
        return parse_response(res)

    def put(self, path: str, body: Dict[str, str], headers: Dict[str, str] = None) -> Union[Dict[str, Any], None]:
        res = requests.put(f'{self.base_url}{path}', json=body, headers=headers)
        return parse_response(res)

    def delete(self, path: str, headers: Dict[str, str] = None) -> Union[Dict[str, Any], None]:
        res = requests.delete(f'{self.base_url}{path}', headers=headers)
        return parse_response(res)

    def create_user_music(self, param):
        pass
