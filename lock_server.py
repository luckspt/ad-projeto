#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_server.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer importação
from argparse import ArgumentParser
from typing import Dict, Union, Tuple
from lock_pool import lock_pool
import sock_utils

###############################################################################


# código do programa principal


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


def main() -> None:
    try:
        args = parse()

        socket = sock_utils.create_tcp_server_socket(args['address'], args['port'], 1)
        while True:
            (conn_sock, (addr, port)) = socket.accept()

            print(f'Ligado a {addr} no porto {port}')

            msg = conn_sock.recv(1024)

            res = [10, 'blabla']

            parsed_res = ' '.join(res)
            conn_sock.sendall(parsed_res.encode('utf-8'))
            conn_sock.close()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
