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
import sqlite3
from flask import Flask, g, request
from argparse import ArgumentParser
from typing import Dict, Union, Tuple

###############################################################################


# código do programa principal

def connect_db():
    db_is_created = isfile('playlists.db')
    connection = sqlite3.connect('playlists.db')
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
    parser = ArgumentParser(description='Servidor de recursos')

    parser.add_argument("address", help="IP ou Hostname onde o Servidor irá fornecer os recursos")

    parser.add_argument("port", help="Porto TCP onde escutará por pedidos de ligação", type=int)

    parser.add_argument("n", help="Número de recursos que serão geridos pelo Servidor", type=int)

    parser.add_argument("k", help="Número de bloqueios permitidos em cada recurso", type=int)

    args = parser.parse_args().__dict__

    return args


app = Flask(__name__)

# TODO perguntar ao prof
@app.before_request
def before_request():
    conn, cursor = connect_db()

    # Store as globals
    g.conn = conn
    g.cursor = cursor

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        print('Index')
        return {'data': g.cursor.execute('SELECT * FROM utilizadores').fetchall()}
    elif request.method == 'POST':
        print('Index POST')
        g.cursor.execute('INSERT INTO utilizadores VALUES (?, ?)', ('lucas', 'lucas'))
        g.conn.commit()

        return {'data': 'ok'}, 201

def main() -> None:
    """
    Programa principal
    """
    try:
        # args = parse()
        app.run()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
