"""
Aplicações Distribuídas - Projeto 4 - client/playlists.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""
from reqs import Reqs


class Playlists:
    api: Reqs = None

    def __init__(self, api: Reqs) -> None:
        self.api = api

    def create_artist(self, id_spotify: str):
        data = {
            'id_spotify': id_spotify
        }

        return self.api.post('/artistas', data)

    def create_music(self, id_spotify: str):
        data = {
            'id_spotify': id_spotify
        }

        return self.api.post('/musicas', data)

    def create_user(self, name: str, password: str):
        data = {
            'nome': name,
            'senha': password
        }

        return self.api.post('/utilizadores', data)

    def create_user_rating(self, id_user: int, id_music: int, rating: str):
        data = {
            'musica': id_music,
            'avaliacao': rating
        }

        return self.api.post(f'/utilizadores/{id_user}/avaliacoes', data)

    def delete_all_artists(self):
        return self.api.delete('/artistas')

    def delete_all_musics_artist(self, id_artist: int):
        return self.api.delete(f'/artistas/{id_artist}/musicas')

    def delete_all_musics_user(self, id_user: int):
        return self.api.delete(f'/utilizadores/{id_user}/musicas')

    def delete_all_musics(self, rating: str = None):
        if rating is None:
            return self.api.delete('/musicas')
        else:
            return self.api.delete(f'/avaliacoes/{rating}/musicas')

    def delete_all_users(self):
        return self.api.delete('/utilizadores')

    def delete_artist(self, id_artist: int):
        return self.api.delete(f'/artistas/{id_artist}')

    def delete_music(self, id_music: int):
        return self.api.delete(f'/musicas/{id_music}')

    def delete_user(self, id_user: int):
        return self.api.delete(f'/utilizadores/{id_user}')

    def get_all_artists(self):
        return self.api.get('/artistas')

    def get_all_musics_artist(self, id_artist: int):
        return self.api.get(f'/artistas/{id_artist}/musicas')

    def get_all_musics_user(self, id_user: int):
        return self.api.get(f'/utilizadores/{id_user}/musicas')

    def get_all_musics(self, rating: str = None):
        if rating is None:
            return self.api.get('/musicas')
        else:
            return self.api.get(f'/avaliacoes/{rating}/musicas')

    def get_all_users(self):
        return self.api.get('/utilizadores')

    def get_artist(self, id_artist: int):
        return self.api.get(f'/artistas/{id_artist}')

    def get_music(self, id_music: int):
        return self.api.get(f'/musicas/{id_music}')

    def get_user(self, id_user: int):
        return self.api.get(f'/utilizadores/{id_user}')

    def update_music(self, id_music: int, rating: str, id_user: int):
        data = {
            'avaliacao': rating,
        }

        return self.api.put(f'/utilizadores/{id_user}/avaliacoes/{id_music}', data)

    def update_user(self, id_user: int, password: str):
        data = {
            'password': password
        }

        return self.api.put(f'/utilizadores/{id_user}', data)
