#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 4 - server/main.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer importação
from os.path import isfile
from sqlite3 import Cursor, Row, connect, Connection, sqlite_version_info
import sqlite3
from flask import Flask, request, redirect
from argparse import ArgumentParser
from typing import Any, Dict, List, Union, Tuple
from werkzeug.exceptions import HTTPException
from spotify import Spotify
from exceptions import ApiException
from dotenv import load_dotenv
from os import getenv
import ssl

load_dotenv()

###############################################################################
AVALIACOES = {'M', 'm', 'S', 'B', 'MB'}
DBNAME = 'playlists.db'

spotify = Spotify(getenv('SPOTIFY_CLIENT_ID'), getenv('SPOTIFY_CLIENT_SECRET'))

db: Connection = None
cursor: Cursor = None
# código do programa principal


def force_params(body: Dict[str, Any], keys: List[str], name: str) -> None:
    for key in keys:
        if key not in body:
            raise ApiException(
                f'"{key}" é obrigatório', f'"{key}" é obrigatório num objeto {name}', http_code=400)


def connect_db() -> Tuple[Connection, Cursor]:
    global db, cursor

    db = connect(DBNAME, check_same_thread=False)
    db.row_factory = Row

    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

def get_avaliacao_id(avaliacao, cursor):
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
    return id_avaliacao


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

    response = {
        'describedBy': error.described_by,
        'supportId': error.support_id,
        'httpStatus': error.http_code,
        'title': error.title,
        'detail': error.detail,
    }

    return response, error.http_code, headers


@app.errorhandler(HTTPException)
def handle_generic_err(e: HTTPException):
    return handle_api_err(ApiException(e.name, e.description, e.code))

# ------------------------------------

# ------------------------------------
# ---- Auth


@app.route('/login', methods=["GET"])
def login():
    auth_url = spotify.authorize()
    return redirect(auth_url)


@app.route('/callback', methods=["GET"])
def callback():
    spotify.fetch_token(request.url)
    return redirect('/profile')


@app.route('/profile', methods=["GET"])
def profile():
    return spotify.me()

# ------------------------------------
# ---- Utilizadores


@app.route('/utilizadores', methods=['GET', 'POST', 'DELETE'])
def utilizadores_endpoint():
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

        try:
            cursor.execute(
                'INSERT INTO utilizadores (nome, senha) VALUES (?, ?) RETURNING *', (nome, senha))
            utilizador = cursor.fetchone()
            db.commit()

            return {
                'utilizador': dict(utilizador)
            }, 201
        except sqlite3.IntegrityError:
            raise ApiException(
                'Utilizador já existe', f'O utilizador "{nome}" já existe', http_code=409)
    elif request.method == 'DELETE':
        # ELIMINAR utilizadores
        cursor.execute('DELETE FROM utilizadores')
        db.commit()

        return '', 204


@app.route('/utilizadores/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def utilizador_endpoint(uid: int):
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


@app.route('/utilizadores/<int:uid>/musicas', methods=['GET', 'DELETE'])
def utilizador_musicas_endpoint(uid: int):
    cursor.execute('SELECT * FROM utilizadores WHERE id = ?', (uid,))
    utilizador = cursor.fetchone()
    if utilizador is None:
        raise ApiException('Utilizador não encontrado',
                           f'Utilizador com id "{uid}" não encontrado', http_code=404)

    if request.method == 'GET':
        cursor.execute(
            'SELECT * FROM musicas WHERE id IN (SELECT id_musica FROM playlists WHERE id_user = ?)', (uid,))
        musicas = cursor.fetchall() or ()

        return {
            'musicas': list(map(dict, musicas))
        }
    elif request.method == 'DELETE':
        # ELIMINAR todas as musicas de um utilizador
        cursor.execute(
            'DELETE FROM musicas WHERE id IN (SELECT id_musica FROM playlists WHERE id_user = ?)', (uid,))
        db.commit()

        return '', 204


@app.route('/utilizadores/<int:uid>/avaliacoes', methods=['POST'])
def utilizador_avaliacoes_endpoint(uid: int):
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
        id_avaliacao = get_avaliacao_id(avaliacao, cursor)

        try:
            cursor.execute(
                'INSERT INTO playlists (id_user, id_musica, id_avaliacao) VALUES (?, ?, ?) RETURNING *',
                (uid, musica, id_avaliacao))
            avaliacao = cursor.fetchone()
            db.commit()

            avaliacao = dict(avaliacao)
            del avaliacao['id_avaliacao']
            avaliacao['avaliacao'] = body['avaliacao']

            return {
                'avaliacao': avaliacao
            }, 201
        except sqlite3.IntegrityError:
            raise ApiException(
                'Erro de integridade', f'O utilizador "{uid}" ou a música "{musica}" não existem ou já existe uma avaliação do utilizador "{uid}" para a música "{musica}"', http_code=409)


@app.route('/utilizadores/<int:uid>/avaliacoes/<int:mid>', methods=['PUT'])
def utilizador_avaliacao_endpoint(uid: int, mid: int):
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
    id_avaliacao = get_avaliacao_id(avaliacao, cursor)

    try:
        cursor.execute(
            'UPDATE playlists SET id_avaliacao = ? WHERE id_user = ? AND id_musica = ? RETURNING *',
            (id_avaliacao, uid, mid))
        avaliacao = cursor.fetchone()
        db.commit()

        avaliacao = dict(avaliacao)
        del avaliacao['id_avaliacao']
        avaliacao['avaliacao'] = body['avaliacao']

        return {
            'avaliacao': avaliacao
        }, 200
    except sqlite3.IntegrityError:
        raise ApiException(
            'Erro de integridade', f'O utilizador "{uid}" ou a música "{mid}" não existem ou a avaliação do utilizador "{uid}" para a música "{mid}" não existe', http_code=409)


# ------------------------------------

# ------------------------------------
# ---- Artistas


@app.route('/artistas', methods=['GET', 'POST', 'DELETE'])
def artistas_endpoint():
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

        try:
            cursor.execute(
                'INSERT INTO artistas (id_spotify, nome) VALUES (?, ?) RETURNING *', (id_spotify, artista['name']))
            artista = cursor.fetchone()
            db.commit()

            return {
                'artista': dict(artista)
            }, 201
        except sqlite3.IntegrityError:
            raise ApiException(
                'Erro de integridade', f'O artista "{id_spotify}" já existe', http_code=409)

    elif request.method == 'DELETE':
        # ELIMINAR artistas
        cursor.execute('DELETE FROM artistas')
        db.commit()

        return '', 204


@app.route('/artistas/<int:aid>', methods=['GET', 'DELETE'])
def artista_endpoint(aid: int):
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

        try:
            cursor.execute('INSERT INTO musicas (id_spotify, nome, id_artista) VALUES (?, ?, ?) RETURNING *',
                             (musica['id'], musica['name'], artista['id']))
            musica = cursor.fetchone()
            db.commit()

            return {
                'musica': dict(musica)
            }, 201
        except sqlite3.IntegrityError:
            raise ApiException(
                'Erro de integridade', f'A música "{id_spotify}" já existe', http_code=409)

    elif request.method == 'DELETE':
        # ELIMINAR musicas
        cursor.execute('DELETE FROM musicas')
        db.commit()

        return '', 204


@app.route('/musicas/<int:mid>', methods=['GET', 'DELETE'])
def musica_endpoint(mid: int):
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
        # Pré requisitos
        if sqlite_version_info < (3, 35, 0):
            raise RuntimeError(
                'SQLite 3.35.0 ou superior é necessário (ver README.txt)')

        args = parse()

        db_created = isfile(DBNAME)
        if not db_created:
            with open('schema.sql', 'r') as fschema:
                schema = fschema.read()
                
                connect_db()
                cursor.executescript(schema)
                db.commit()
        
        # Pode ter sido definido no if acima
        if db is None:
            connect_db()

        context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile='../certs/root.pem')
        context.load_cert_chain(
            certfile='../certs/serv.crt', keyfile='../certs/serv.key')

        spotify.api.redirect_uri = f'https://{args["address"]}:{args["port"]}/callback'
        app.run(args['address'], args['port'],
                debug=args['debug'], ssl_context=context)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
