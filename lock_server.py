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
        pool = lock_pool(args['n'], args['k'])
        while True:
            (conn_sock, (addr, port)) = socket.accept()

            print(f'Ligado a {addr} no porto {port}')

            msg = conn_sock.recv(1024)
            cmd, *cargs = msg.decode('utf-8').split()

            res = []

            pool.clear_expired_locks()

            try:
                if len(cmd) == 0:
                    raise Exception('UNKNOWN COMMAND')

                if cmd == 'LOCK':
                    if len(cargs) < 4:
                        raise Exception('LOCK type, resource_id, time_limit, and client_id are required')
                    elif len(cargs) > 4:
                        raise Exception('LOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('LOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('LOCK resource_id must be a digit')

                    if not cargs[2].isdigit():
                        raise Exception('LOCK time_limit must be a digit')

                    if not cargs[3].isdigit():
                        raise Exception('LOCK client_id must be a digit')

                    resp = pool.lock(cargs[0], int(cargs[1]), cargs[3], int(cargs[2]))
                    res.append(resp)
                elif cmd == 'UNLOCK':
                    if len(cargs) < 3:
                        raise Exception('UNLOCK type, resource_id, and client_id are required')
                    elif len(cargs) > 3:
                        raise Exception('UNLOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('UNLOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('UNLOCK resource_id must be a digit')

                    if not cargs[2].isdigit():
                        raise Exception('UNLOCK client_id must be a digit')

                    resp = pool.unlock(cargs[0], int(cargs[1]), cargs[2])
                    res.append(resp)
                elif cmd == 'STATUS':
                    if len(cargs) < 1:
                        raise Exception('STATUS resource_id is required')

                    resp = pool.status(int(cargs[0]))
                    res.append(resp)
                elif cmd == 'STATS':
                    if len(cargs) < 1:
                        raise Exception('STATS subcommand is required')
                    scmd, *sargs = cargs

                    if scmd == 'K':
                        if len(sargs) < 1:
                            raise Exception('STATS resource_id is required')
                        elif len(sargs) > 1:
                            raise Exception('STATS too many arguments')
                    elif scmd == 'N':
                        if len(cargs) > 1:
                            raise Exception('STATS too many arguments')
                    elif scmd == 'D':
                        if len(cargs) > 1:
                            raise Exception('STATS too many arguments')
                    else:
                        raise Exception('STATS subcommand must be K, N, or D')

                    resp = pool.stats(scmd, int(sargs[0]) if scmd == 'K' else None)
                    res.append(str(resp))
                elif cmd == 'PRINT':
                    res.append(str(pool))
            except Exception as e:
                print(e)
                continue

            parsed_res = ' '.join(res)
            conn_sock.sendall(parsed_res.encode('utf-8'))
            conn_sock.close()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
