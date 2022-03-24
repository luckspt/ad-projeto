#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_server.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer importação
import pickle
import struct
from argparse import ArgumentParser
from typing import Dict, Union, Tuple
from lock_skel import lock_skel
import select as sel
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
        skel = lock_skel(args['n'], args['k'])

        listen_socket = sock_utils.create_tcp_server_socket(args['address'], args['port'], 1)

        socket_list = [listen_socket]

        while True:
            R, W, X = sel.select(socket_list, [], [])
            for sckt in R:
                if sckt is listen_socket:
                    conn_sock, addr = sckt.accept()
                    addr, port = conn_sock.getpeername()
                    print(f'\n------------------------\nLigado a {addr} no porto {port}')
                    socket_list.append(conn_sock)
                else:
                    res_size_bytes = sock_utils.receive_all(sckt, 4)

                    if len(res_size_bytes):
                        size = struct.unpack('i', res_size_bytes)[0]
                        req_bytes = sock_utils.receive_all(sckt, size)

                        resp = skel.processMessage(req_bytes)

                        size_bytes = struct.pack('i', len(resp))
                        sckt.sendall(size_bytes)
                        sckt.sendall(resp)
                    else:  # isto pq o TCP tem o protocolo de finalização, e o select desbloqueia com uma mensagem vazia
                        sckt.close()
                        socket_list.remove(sckt)
                        print('Cliente fechou a ligação\n------------------------\n')
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
