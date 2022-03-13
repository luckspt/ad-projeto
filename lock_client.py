#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 1 - lock_client.py
Grupo: 21
Números de aluno: 56895, 56926
"""
# Zona para fazer imports
from argparse import ArgumentParser
from time import sleep
from typing import Dict, Union, Tuple
import net_client


# Programa principal


def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(description='Cliente de um Servidor de recursos')

    parser.add_argument("client_id", help="ID único do Cliente")

    parser.add_argument("address", help="IP ou Hostname do Servidor que fornece os recursos")

    parser.add_argument("port", help="Porto TCP onde o Servidor recebe conexões", type=int)

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
                    elif len(cargs) > 1:
                        raise Exception('SLEEP too many arguments')

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
                    elif len(cargs) > 3:
                        raise Exception('LOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('LOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('LOCK resource_id must be a digit')

                    if not cargs[2].isdigit():
                        raise Exception('LOCK time_limit must be a digit')

                    cargs.append(args['client_id'])
                elif cmd == 'UNLOCK':
                    if len(cargs) < 2:
                        raise Exception('UNLOCK type and resource_id are required')
                    elif len(cargs) > 2:
                        raise Exception('UNLOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('UNLOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('UNLOCK resource_id must be a digit')

                    cargs.append(args['client_id'])
                elif cmd == 'STATUS':
                    if len(cargs) < 1:
                        raise Exception('STATUS resource_id is required')
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
                        if len(sargs) > 0:
                            raise Exception('STATS too many arguments')
                    elif scmd == 'D':
                        if len(sargs) > 0:
                            raise Exception('STATS too many arguments')
                    else:
                        raise Exception('STATS subcommand must be K, N, or D')
                elif cmd == 'PRINT':
                    if len(cargs) > 0:
                        raise Exception('PRINT too many arguments')
                else:
                    raise Exception('UNKNOWN COMMAND')
            
                cmd_parsed = ' '.join([cmd, *cargs])

                client.connect()
                res = client.send_receive(cmd_parsed)
                client.close()

                print(res)
            except Exception as e:
                print(e)
                continue

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
