#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 3 - lock_server.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer importação
from crypt import methods
from os.path import isfile
from sqlite3 import Cursor, connect, Connection
from flask import Flask, g, request
from argparse import ArgumentParser
from typing import Dict, Union, Tuple

###############################################################################


# código do programa principal

def connect_db() -> Tuple[Connection, Cursor]:
    db_is_created = isfile('playlists.db')
    connection = connect('playlists.db')
    cursor = connection.cursor()

    if not db_is_created:
        with open('schema.sql', 'r') as fschema:
            schema = fschema.read()
            cursor.executescript(schema)
        connection.commit()

    return connection, cursor



def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(description='API Flask de um Serviço de Playlists')

    parser.add_argument("address", help="IP ou Hostname onde o Servidor irá fornecer os recursos")

    parser.add_argument("port", help="Porto TCP onde o Servidor irá fornecer os recursos", type=int)

    args = parser.parse_args().__dict__

    return args


app = Flask(__name__)

# TODO perguntar ao prof
@app.before_request
def before_request():
    conn, cursor = connect_db()

    # Store as globals
    g.db = conn
    g.cursor = cursor

# ------------------------------------
# ---- Utilizadores
@app.route('/utilizadores', methods=['GET', 'POST', 'DELETE'])
def users():
    if request.method == 'GET':
        # GET ALL utilizadores
        pass
    elif request.method == 'POST':
        # CRIAR utilizador
        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR utilizadores
        pass

@app.route('/utilizadores/<int:u_id>', methods=['GET', 'PUT', 'DELETE'])
def user(u_id: int):
    if request.method == 'GET':
        # GET DETAILS de utilizador singular
        pass
    elif request.method == 'PUT':
        # ATUALIZAR utilizador singular
        pass
    elif request.method == 'DELETE':
        # ELIMINAR utilizador singular
        pass

@app.route('/utilizadores/<int:u_id>/avaliacoes', methods=['GET', 'POST', 'DELETE'])
def user_avaliacoes(u_id: int):
    # TODO isto ou o GET /musicas?uid=123, pq o CREATE é <id_user> <id_musica> <avaliacao> mas o update é MUSIC <id_musica> <avaliacao> <id_user>, que faz com que o update seja feito na música e não no utilizador
    if request.method == 'GET':
        # GET avaliacoes do utilizador
        pass
    elif request.method == 'POST':
        # CRIAR avaliação
        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR avaliações do utilizador
        pass
# ------------------------------------

# ------------------------------------
# ---- Artistas
@app.route('/artistas', methods=['GET', 'POST', 'DELETE'])
def artistas():
    if request.method == 'GET':
        # GET ALL artistas
        pass
    elif request.method == 'POST':
        # CRIAR artista
        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR artistas
        pass

@app.route('/artistas/<int:a_id>', methods=['GET', 'DELETE'])
def artista(a_id: int):
    if request.method == 'GET':
        # GET DETAILS de artista singular
        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR artista singular
        pass
# ------------------------------------

# ------------------------------------
# ---- Músicas
@app.route('/musicas', methods=['GET', 'POST', 'DELETE'])
def musicas():
    if request.method == 'GET':
        # TODO perguntar se usamos query string para limitar às músicas do artista x (e o mesmo para utilizador e avaliação)
        # GET ALL músicas
        pass
    elif request.method == 'POST':
        # CRIAR música
        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR artistas
        pass

@app.route('/musicas/<int:m_id>', methods=['GET', 'DELETE'])
def musica(m_id: int):
    if request.method == 'GET':
        # GET DETAILS de música singular
        pass
    elif request.method == 'DELETE':
        # TODO perguntar se é eliminar tudo ou se recebe uma lista no body
        # ELIMINAR música singular
        pass
# ------------------------------------


def main() -> None:
    """
    Programa principal
    """
    try:
        args = parse()
        app.run(args['address'], args['port'], debug=True)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
