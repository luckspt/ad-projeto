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
import sqlite3
from flask import Flask, request
from argparse import ArgumentParser
from typing import Any, Dict, List, Union, Tuple

from werkzeug.exceptions import HTTPException
from spotify import Spotify
from exceptions import ApiException

###############################################################################
AVALIACOES = {'M', 'm', 'S', 'B', 'MB'}
spotify = Spotify()

# código do programa principal


def force_params(body: Dict[str, Any], keys: List[str], name: str) -> None:
    for key in keys:
        if key not in body:
            raise ApiException(
                f'"{key}" é obrigatório', f'"{key}" é obrigatório num objeto {name}', http_code=400)


def connect_db(filename='playlists.db') -> Tuple[Connection, Cursor]:
    db_is_created = isfile(filename)
    db = connect(filename)
    db.row_factory = Row

    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

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
@app.errorhandler(ApiException)
def handle_api_err(error: ApiException):
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


@app.errorhandler(HTTPException)
def handle_generic_err(e: HTTPException):
    return handle_api_err(ApiException(e.name, e.description, e.code))


@app.errorhandler(sqlite3.IntegrityError)
def handle_sqlite_err(e: sqlite3.IntegrityError):
    return handle_api_err(ApiException(
        'Erro de integridade',
        e.args[0],
        400
    ))

# ------------------------------------

# ------------------------------------
# ---- Utilizadores


@app.route('/utilizadores', methods=['GET', 'POST', 'DELETE'])
def utilizadores_endpoint():
    db, cursor = connect_db()

    if request.method == 'GET':
        # LISTAR utilizadores
        cursor.execute('SELECT * FROM utilizadores')

        utilizadores = cursor.fetchall() or ()

        return {
            'utilizador': list(map(dict, utilizadores))
        }
    elif request.method == 'POST':
        # CRIAR utilizador
        body = request.get_json()
        force_params(body, ['nome', 'senha'], 'utilizador')

        nome, senha = body["nome"], body["senha"]

        cursor.execute(
            'INSERT INTO utilizadores (nome, senha) VALUES (?, ?) RETURNING *', (nome, senha))
        utilizador = cursor.fetchone()
        db.commit()


        return {
            'utilizador': dict(utilizador)
        }, 201
    elif request.method == 'DELETE':
        # ELIMINAR utilizadores
        cursor.execute('DELETE FROM utilizadores')
        db.commit()

        return '', 204


@app.route('/utilizadores/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def utilizador_endpoint(uid: int):
    db, cursor = connect_db()

    cursor.execute('SELECT * FROM utilizadores WHERE id = ?', (uid,))
    utilizador = cursor.fetchone()
    if utilizador is None:
        raise ApiException('Utilizador não encontrado',
                           f'Utilizador com id "{uid}" não encontrado', http_code=404)

    if request.method == 'GET':
        # DETAILS de utilizador singular
        return dict(utilizador)
    elif request.method == 'PUT':
        # ATUALIZAR utilizador singular
        body = request.get_json()
        force_params(body, ['senha'], 'utilizador')

        senha = body["senha"]

        cursor.execute(
            'UPDATE utilizadores SET senha = ? WHERE id = ? RETURNING *', (senha, uid))
        utilizador = cursor.fetchone()
        db.commit()

        return {
            'utilizador': dict(utilizador)
        }, 200
    elif request.method == 'DELETE':
        # ELIMINAR utilizador singular
        cursor.execute('DELETE FROM utilizadores WHERE id = ?', (uid,))
        db.commit()

        return '', 204


@app.route('/utilizadores/<int:uid>/avaliacoes', methods=['POST'])
def utilizador_musicas_endpoint(uid: int):
    db, cursor = connect_db()

    cursor.execute('SELECT * FROM utilizadores WHERE id = ?', (uid,))
    utilizador = cursor.fetchone()
    if utilizador is None:
        raise ApiException('Utilizador não encontrado',
                           f'Utilizador com id "{uid}" não encontrado', http_code=404)

    if request.method == 'POST':
        # CRIAR avaliação de utilizador singular
        body = request.get_json()
        force_params(body, ['musica', 'avaliacao'], 'avaliacao')

        musica, avaliacao = body["musica"], body["avaliacao"]
        if avaliacao not in AVALIACOES:
            raise ApiException(
                'Avaliação inválida', f'A avaliação "{avaliacao}" é inválida', http_code=400)

        cursor.execute(
            'SELECT id FROM avaliacoes WHERE sigla = ?', (avaliacao,))
        id_avaliacao = cursor.fetchone()
        if not id_avaliacao:
            raise ApiException(
                'Avaliação inválida', f'A avaliação "{avaliacao}" é inválida', http_code=400)
        id_avaliacao = dict(id_avaliacao)['id']

        cursor.execute(
            'INSERT INTO playlists (id_user, id_musica, id_avaliacao) VALUES (?, ?, ?) RETURNING *', (uid, musica, id_avaliacao))
        avaliacao = cursor.fetchone()
        db.commit()

        avaliacao = dict(avaliacao)
        del avaliacao['id_avaliacao'] 
        avaliacao['avaliacao'] = body['avaliacao']

        return {
            'avaliacao': avaliacao
        }, 201


@app.route('/utilizadores/<int:uid>/avaliacoes/<int:mid>', methods=['PUT'])
def utilizador_avaliacao_endpoint(uid: int, mid: int):
    db, cursor = connect_db()

    cursor.execute('SELECT * FROM utilizadores WHERE id = ?', (uid,))
    utilizador = cursor.fetchone()
    if utilizador is None:
        raise ApiException('Utilizador não encontrado',
                           f'Utilizador com id "{uid}" não encontrado', http_code=404)

    cursor.execute(
        'SELECT * FROM playlists WHERE id_user = ? AND id_musica = ?', (uid, mid))
    db_avaliacao = cursor.fetchone()
    if db_avaliacao is None:
        raise ApiException('Avaliação não encontrada',
                           f'Avaliação com id_user "{uid}" e id_musica "{mid}" não encontrada', http_code=404)

    body = request.get_json()
    force_params(body, ['avaliacao'], 'avaliacao')

    avaliacao = body["avaliacao"]
    if avaliacao not in AVALIACOES:
        raise ApiException(
            'Avaliação inválida', f'A avaliação "{avaliacao}" é inválida', http_code=400)

    cursor.execute('SELECT id FROM avaliacoes WHERE sigla = ?', (avaliacao,))
    id_avaliacao = cursor.fetchone()
    if not id_avaliacao:
        raise ApiException(
            'Avaliação inválida', f'A avaliação "{avaliacao}" é inválida', http_code=400)
    id_avaliacao = dict(id_avaliacao)['id']

    cursor.execute(
        'UPDATE playlists SET id_avaliacao = ? WHERE id_user = ? AND id_musica = ? RETURNING *', (id_avaliacao, uid, mid))
    avaliacao = cursor.fetchone()
    db.commit()

    avaliacao = dict(avaliacao)
    del avaliacao['id_avaliacao'] 
    avaliacao['avaliacao'] = body['avaliacao']

    return {
        'avaliacao': avaliacao
    }, 200

# ------------------------------------

# ------------------------------------
# ---- Artistas


@app.route('/artistas', methods=['GET', 'POST', 'DELETE'])
def artistas_endpoint():
    db, cursor = connect_db()

    if request.method == 'GET':
        # LISTAR artistas
        cursor.execute('SELECT * FROM artistas')
        artistas = cursor.fetchall() or ()

        return {
            'artistas': list(map(dict, artistas))
        }
    elif request.method == 'POST':
        # CRIAR artista
        body = request.get_json()

        force_params(body, ['id_spotify'], 'artista')

        id_spotify = body["id_spotify"]

        artista = spotify.artist(id_spotify)
        if 'name' not in artista:
            raise ApiException(
                'Artista não encontrado', f'Artista com id_spotify "{id_spotify}" não encontrado', http_code=404)

        cursor.execute(
            'INSERT INTO artistas (id_spotify, nome) VALUES (?, ?) RETURNING *', (id_spotify, artista['name']))
        artista = cursor.fetchone()
        db.commit()

        return {
            'artista': dict(artista)
        }, 201

    elif request.method == 'DELETE':
        # ELIMINAR artistas
        cursor.execute('DELETE FROM artistas')
        db.commit()

        return '', 204


@app.route('/artistas/<int:aid>', methods=['GET', 'DELETE'])
def artista_endpoint(aid: int):
    db, cursor = connect_db()

    cursor.execute('SELECT * FROM artistas WHERE id = ?', (aid,))
    artista = cursor.fetchone()
    if artista is None:
        raise ApiException('Artista não encontrado',
                           f'Artista com id "{aid}" não encontrado', http_code=404)

    if request.method == 'GET':
        # GET DETAILS de artista singular
        return dict(artista)
    elif request.method == 'DELETE':
        # ELIMINAR artista singular
        cursor.execute('DELETE FROM artistas WHERE id = ?', (aid,))
        db.commit()

        return '', 204


@app.route('/artistas/<int:aid>/musicas', methods=['GET', 'DELETE'])
def artista_musicas_endpoint(aid: int):
    db, cursor = connect_db()

    cursor.execute('SELECT * FROM artistas WHERE id = ?', (aid,))
    artista = cursor.fetchone()
    if artista is None:
        raise ApiException('Artista não encontrado',
                           f'Artista com id "{aid}" não encontrado', http_code=404)

    if request.method == 'GET':
        # LISTAR musicas de artista singular
        cursor.execute(
            'SELECT * FROM musicas WHERE id_artista = ?', (aid,))
        musicas = cursor.fetchall() or ()

        return {
            'musicas': list(map(dict, musicas))
        }
    elif request.method == 'DELETE':
        # ELIMINAR musicas de artista singular
        cursor.execute('DELETE FROM musicas WHERE id_artista = ?', (aid,))
        db.commit()

        return '', 204
# ------------------------------------

# ------------------------------------
# ---- Músicas


@app.route('/musicas', methods=['GET', 'POST', 'DELETE'])
def musicas_endpoint():
    db, cursor = connect_db()

    if request.method == 'GET':
        # LISTAR músicas
        cursor.execute('SELECT * FROM musicas')
        musicas = cursor.fetchall() or ()

        return {
            'musicas': list(map(dict, musicas))
        }
    elif request.method == 'POST':
        # CRIAR música
        body = request.get_json()
        force_params(body, ['id_spotify'], 'musica')

        id_spotify = body['id_spotify']

        musica = spotify.track(id_spotify)
        if 'name' not in musica:
            raise ApiException(
                'Música não encontrada', f'Música com id_spotify "{id_spotify}" não encontrada', http_code=404)

        # Tratar do Artista
        s_artista = musica['artists'][0]
        cursor.execute(
            'SELECT * FROM artistas WHERE id_spotify = ?', (s_artista['id'],))
        artista = cursor.fetchone()

        if not artista:
            # Artista não existe na bd ainda
            cursor.execute('INSERT INTO artistas (id_spotify, nome) VALUES (?, ?)',
                           (s_artista['id'], s_artista['name']))
            db.commit()

            artista = {'id': cursor.lastrowid}

        cursor.execute('INSERT INTO musicas (id_spotify, nome, id_artista) VALUES (?, ?, ?) RETURNING *',
                       (musica['id'], musica['name'], artista['id']))
        musica = cursor.fetchone()
        db.commit()

        return {
            'musica': dict(musica)
        }, 201

    elif request.method == 'DELETE':
        # ELIMINAR musicas
        cursor.execute('DELETE FROM musicas')
        db.commit()

        return '', 204


@app.route('/musicas/<int:mid>', methods=['GET', 'DELETE'])
def musica_endpoint(mid: int):
    db, cursor = connect_db()

    cursor.execute('SELECT * FROM musicas WHERE id = ?', (mid,))
    musica = cursor.fetchone()
    if musica is None:
        raise ApiException('Música não encontrada',
                           f'Música com id "{mid}" não encontrada', http_code=404)

    if request.method == 'GET':
        # GET DETAILS de música singular
        return dict(musica)
    elif request.method == 'DELETE':
        # ELIMINAR música singular
        cursor.execute('DELETE FROM musicas WHERE id = ?', (mid,))
        db.commit()

        return '', 204


# ------------------------------------
# Avaliacoes -------------------------
@app.route('/avaliacoes/<aid>/musicas', methods=['GET', 'DELETE'])
def avaliacao_musicas_endpoint(aid: str):
    if aid not in AVALIACOES:
        raise ApiException(f'Avaliação inválida',
                           f'A avaliação "{aid}" não é válida', http_code=404)

    db, cursor = connect_db()

    cursor.execute('SELECT id FROM avaliacoes WHERE sigla = ?', (aid,))
    avaliacao = cursor.fetchone()
    if not avaliacao:
        raise ApiException(
            'Avaliação inválida', f'A avaliação "{avaliacao}" é inválida', http_code=400)
    avaliacao = dict(avaliacao)['id']

    if request.method == 'GET':
        # LISTAR músicas
        cursor.execute(
            f'SELECT * FROM musicas WHERE id IN (SELECT id_musica FROM playlists WHERE id_avaliacao = ?)', (avaliacao,))
        musicas = cursor.fetchall() or ()

        return {
            'musicas': list(map(dict, musicas))
        }
    elif request.method == 'DELETE':
        # ELIMINAR músicas
        cursor.execute(
            'DELETE FROM musicas WHERE id IN (SELECT id_musica FROM playlists WHERE id_avaliacao = ?)', (avaliacao,))
        db.commit()

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
