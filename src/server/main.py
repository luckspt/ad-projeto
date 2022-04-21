#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 3 - server/main.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer importação
from os.path import isfile
from sqlite3 import Cursor, Row, connect, Connection
from flask import Flask, g, request, make_response

from argparse import ArgumentParser
from typing import Dict, Union, Tuple
from spotify import Spotify
from exceptions import ApiException


###############################################################################
AVALIACOES = {'M', 'm', 'S', 'B', 'MB'}
spotify = Spotify()

# TODO perguntar ao prof:
#  'Cada lista de músicas criada por um utilizador (...)', mas um utilizador só pode ter uma?
#  o described by é para fazer um coiso dummy ou ...
#  eliminar tudo ou se recebe uma lista no body
#  eliminar um artista implica apagar as suas músicas? que elimina as músicas das playlists
#  como é que se mostram as respostas do lado do cliente? mostrar o json? e em caso de erro?
#  (GET /musicas) usamos query string [/musicas?utilizador=1&artista=5] para limitar às músicas do artista x (e o mesmo para utilizador e avaliação)
#  

# código do programa principal


def connect_db() -> Tuple[Connection, Cursor]:
    db_is_created = isfile('playlists.db')
    db = connect('playlists.db')
    db.row_factory = Row

    cursor = db.cursor()

    if not db_is_created:
        with open('schema.sql', 'r') as fschema:
            schema = fschema.read()
            cursor.executescript(schema)
        db.commit()

    return db, cursor


def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(description='API Flask de um Serviço de Playlists')

    parser.add_argument(
        'address',
        help='IP ou Hostname onde o Servidor irá fornecer os recursos',
        default='localhost'
    )

    parser.add_argument(
        'port',
        help='Porto TCP onde o Servidor irá fornecer os recursos',
        type=int,
        default=9999
    )

    parser.add_argument(
        '--debug',
        help='Ativar debug do Flask',
        action='store_true'
    )

    args = parser.parse_args().__dict__

    return args


app = Flask(__name__)

# ------------------------------------
# ---- Hooks
# TODO perguntar ao prof
#  1- o before_request
#  2- se é a cada pedido
#  3- se a conexão é global
@app.before_request
def before_request():
    conn, cursor = connect_db()

    # Store as globals
    g.db = conn
    g.cursor = cursor


@app.errorhandler(ApiException)
def handle_err(error: ApiException):
    headers = {'Content-Type': 'application/api-problem+json'}

    http_code = error.http_code
    response = {
        'describedBy': error.described_by,
        'supportId': error.support_id,
        'httpStatus': http_code,
        'title': error.title,
        'detail': error.detail,
    }

    return response, http_code, headers
# ------------------------------------

# ------------------------------------
# ---- Utilizadores
@app.route('/utilizadores', methods=['GET', 'POST', 'DELETE'])
def users():
    if request.method == 'GET':
        # LISTAR utilizadores
        g.cursor.execute('SELECT * FROM utilizadores')
        utilizadores = g.cursor.fetchall() or ()

        return {
            'utilizador': list(map(dict, utilizadores))
        }
    elif request.method == 'POST':
        # CRIAR utilizador
        body = request.get_json()

        keys = ['nome', 'senha']
        for key in keys:
            if key not in body:
                raise ApiException(
                    f'"{key}" é obrigatório', f'"{key}" é obrigatório num objeto utilizador', http_code=400)

        nome = body["nome"]
        senha = body["senha"]

        g.cursor.execute(
            'INSERT INTO utilizadores (nome, senha) VALUES (?, ?)', (nome, senha))
        g.db.commit()

        return '', 201
    elif request.method == 'DELETE':
        # ELIMINAR utilizadores
        g.cursor.execute('DELETE FROM utilizadores')
        g.db.commit()

        return '', 204


@app.route('/utilizadores/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    g.cursor.execute('SELECT * FROM utilizadores WHERE id = ?', (uid,))
    user = g.cursor.fetchone()
    if user is None:
        raise ApiException('Utilizador não encontrado',
                           f'Utilizador com id "{uid}" não encontrado', http_code=404)

    if request.method == 'GET':
        # DETAILS de utilizador singular
        return dict(user)
    elif request.method == 'PUT':
        # ATUALIZAR utilizador singular
        body = request.get_json()

        keys = ['nome', 'senha']
        for key in keys:
            if key not in body:
                raise ApiException(
                    f'"{key}" é obrigatório', f'"{key}" é obrigatório num objeto utilizador', http_code=400)

        nome = body["nome"]
        senha = body["senha"]

        g.cursor.execute(
            'UPDATE utilizadores SET nome = ?, senha = ? WHERE id = ?', (nome, senha, uid))
        g.db.commit()

        return '', 204
    elif request.method == 'DELETE':
        # ELIMINAR utilizador singular
        g.cursor.execute('DELETE FROM utilizadores WHERE id = ?', (uid,))
        g.db.commit()

        return '', 204


# TODO isto
@app.route('/utilizadores/<int:u_id>/avaliacoes', methods=['GET', 'POST', 'DELETE'])
def user_avaliacoes(u_id: int):
    # TODO isto ou o GET /musicas?uid=123, pq o CREATE é <id_user> <id_musica> <avaliacao> mas o update é MUSIC <id_musica> <avaliacao> <id_user>, que faz com que o update seja feito na música e não no utilizador
    if request.method == 'GET':
        # GET avaliacoes do utilizador
        g.cursor.execute('SELECT id FROM avaliacoes WHERE id = ?', (u_id,))
        u = g.cursor.fetchone()
        if u is None:
            raise ApiException()
        r = make_response(u)
        print(r.headers)  # TODO
        pass
    elif request.method == 'POST':
        # CRIAR avaliação
        # TODO verificar se existe o id
        #sigla = request.json[""]
        #designacao =  request.json[""]
        #g.cursor.execute('INSERT INTO avaliacoes (id, sigla, designacao) VALUES (?, ?, ?)', (u_id, sigla, designacao))

        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR avaliações do utilizador
        g.cursor.execute('DELETE FROM avaliacoes WHERE id = ?', (u_id,))
        r = make_response()
        print(r.headers)  # TODO
        pass
# ------------------------------------

# ------------------------------------
# ---- Artistas
@app.route('/artistas', methods=['GET', 'POST', 'DELETE'])
def artistas():
    if request.method == 'GET':
        # LISTAR artistas
        g.cursor.execute('SELECT * FROM artistas')
        artistas = g.cursor.fetchall() or ()

        return {
            'artistas': list(map(dict, artistas))
        }
    elif request.method == 'POST':
        # CRIAR artista
        body = request.get_json()

        keys = ['id_spotify']
        for key in keys:
            if key not in body:
                raise ApiException(
                    f'"{key}" é obrigatório', f'"{key}" é obrigatório num objeto artista', http_code=400)

        id_spotify = body["id_spotify"]

        artista = spotify.artist(id_spotify)
        if 'name' not in artista:
            raise ApiException(
                'Artista não encontrado', f'Artista com id_spotify "{id_spotify}" não encontrado', http_code=404)

        g.cursor.execute(
            'INSERT INTO artistas (id_spotify, nome) VALUES (?, ?)', (id_spotify, artista['name']))
        g.db.commit()

        return '', 201

    elif request.method == 'DELETE':
        # ELIMINAR artistas
        g.cursor.execute('DELETE FROM artistas')
        g.db.commit()

        return '', 204


@app.route('/artistas/<int:aid>', methods=['GET', 'DELETE'])
def artista(aid: int):
    g.cursor.execute('SELECT * FROM artistas WHERE id = ?', (aid,))
    artista = g.cursor.fetchone()
    if artista is None:
        raise ApiException('Artista não encontrado',
                           f'Artista com id "{aid}" não encontrado', http_code=404)

    if request.method == 'GET':
        # GET DETAILS de artista singular
        return dict(artista)
    elif request.method == 'DELETE':
        # ELIMINAR artista singular
        g.cursor.execute('DELETE FROM artistas WHERE id = ?', (aid,))
        g.db.commit()

        return '', 204
# ------------------------------------

# ------------------------------------
# ---- Músicas
@app.route('/musicas', methods=['GET', 'POST', 'DELETE'])
def musicas():
    if request.method == 'GET':
        # LISTAR músicas
        g.cursor.execute('SELECT * FROM musicas')
        utilizadores = g.cursor.fetchall() or ()

        return {
            'musicas': list(map(dict, utilizadores))
        }
    elif request.method == 'POST':
        # CRIAR música
        body = request.get_json()

        keys = ['id_spotify']
        for key in keys:
            if key not in body:
                raise ApiException(
                    f'"{key}" é obrigatório', f'"{key}" é obrigatório num objeto música', http_code=400)

        id_spotify = body['id_spotify']

        musica = spotify.track(id_spotify)
        if 'name' not in musica:
            raise ApiException(
                'Música não encontrada', f'Música com id_spotify "{id_spotify}" não encontrada', http_code=404)

        # Tratar do Artista
        s_artista = musica['artists'][0]
        g.cursor.execute(
            'SELECT * FROM artistas WHERE id_spotify = ?', (s_artista['id'],))
        artista = g.cursor.fetchone()

        if artista is None:
            # Artista não existe na bd ainda
            g.cursor.execute('INSERT INTO artistas (id_spotify, nome) VALUES (?, ?)',
                             (s_artista['id'], s_artista['name']))
            g.db.commit()

            artista = {'id': g.cursor.lastrowid}

        g.cursor.execute('INSERT INTO musicas (id_spotify, nome, id_artista) VALUES (?, ?, ?)',
                         (musica['id'], musica['name'], artista['id']))
        g.db.commit()

        return '', 201

    elif request.method == 'DELETE':
        # ELIMINAR artistas
        g.cursor.execute('DELETE FROM artistas')
        g.db.commit()

        return '', 204


@app.route('/musicas/<int:mid>', methods=['GET', 'DELETE'])
def musica(mid: int):
    g.cursor.execute('SELECT * FROM musicas WHERE id = ?', (mid,))
    musica = g.cursor.fetchone()
    if musica is None:
        raise ApiException('Música não encontrada',
                           f'Música com id "{mid}" não encontrada', http_code=404)

    if request.method == 'GET':
        # GET DETAILS de música singular
        return dict(musica)
    elif request.method == 'DELETE':
        # ELIMINAR música singular
        g.cursor.execute('DELETE FROM musicas WHERE id = ?', (mid,))
        g.db.commit()

        return '', 204
# ------------------------------------


def main() -> None:
    """
    Programa principal
    """
    try:
        args = parse()
        app.run(args['address'], args['port'], debug=args['debug'])
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
