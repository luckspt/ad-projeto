#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 1 - lock_client.py
Grupo:
Números de aluno:
"""
# Zona para fazer imports
from argparse import ArgumentParser
from time import sleep
from typing import Dict, Union, Tuple, List


# Programa principal
import net_client


def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(description='')

    parser.add_argument("id_cliente", help="ID único do Cliente")

    parser.add_argument("address", help="IP ou Hostname do Servidor que fornece os recursos")

    parser.add_argument("port", help="Porto TCP onde o servidor recebe conexões", type=int)

    args = parser.parse_args().__dict__

    return args


def main() -> None:
    try:
        args = parse()

        client = net_client.server_connection(args['address'], args['port'])
        while True:
            cmd = input('comando > ')
            cmd, *cargs = cmd.split()
            try:
                if len(cmd) == 0:
                    raise Exception('UNKNOWN COMMAND')

                if cmd == 'EXIT':
                    break
                elif cmd == 'SLEEP':
                    if len(cargs) < 1:
                        raise Exception('SLEEP time_limit is required')

                    try:
                        time_limit = float(cargs[0])
                        if time_limit <= 0:
                            raise Exception('SLEEP time_limit must be positive')

                        sleep(time_limit)
                        continue
                    except:
                        raise Exception('SLEEP time_limit must be a float')
                elif cmd == 'LOCK':
                    if len(cargs) < 3:
                        raise Exception('LOCK type, resource_id, and time_limit are required')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('LOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('LOCK resource_id must be a digit')
                elif cmd == 'UNLOCK':
                    if len(cargs) < 2:
                        raise Exception('UNLOCK type and resource_id are required')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('UNLOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('UNLOCK resource_id must be a digit')
                elif cmd == 'STATUS':
                    if len(cargs) < 1:
                        raise Exception('STATUS resource_id is required')
                    pass
                elif cmd == 'STATS':
                    if len(cargs) < 1:
                        raise Exception('STATS subcommand is required')

                    if cargs[0] == 'K':
                        pass
                    elif cargs[0] == 'N':
                        pass
                    if cargs[0] == 'D':
                        pass
                    else:
                        raise Exception('STATS subcommand must be K, N, or D')
                elif cmd == 'PRINT':
                    pass
                else:
                    raise Exception('UNKNOWN COMMAND')
            except Exception as e:
                print(e)
                continue

            client.connect()
            res = client.send_receive(cmd)
            client.close()

            # TODO Trabalhar a resposta

    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
