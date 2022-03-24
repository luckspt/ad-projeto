#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_client.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""
# Zona para fazer imports
from argparse import ArgumentParser
from time import sleep
from typing import Dict, Union, Tuple
from lock_stub import lock_stub


# Programa principal


def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(description='Cliente de um Servidor de recursos')

    parser.add_argument("client_id", help="ID único do Cliente", type=int)

    parser.add_argument("address", help="IP ou Hostname do Servidor que fornece os recursos")

    parser.add_argument("port", help="Porto TCP onde o Servidor recebe conexões", type=int)

    args = parser.parse_args().__dict__

    return args


def main() -> None:
    try:
        args = parse()
        stub = lock_stub(args['address'], args['port'])
        stub.connect()

        while True:
            cmdinp = input('comando > ')

            cmd, *cargs = cmdinp.split()

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

                if cmd == 'LOCK':
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

                    res = stub.lock(cargs[0], int(cargs[1]), int(cargs[2]), args['client_id'])
                elif cmd == 'UNLOCK':
                    if len(cargs) < 2:
                        raise Exception('UNLOCK type and resource_id are required')
                    elif len(cargs) > 2:
                        raise Exception('UNLOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('UNLOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('UNLOCK resource_id must be a digit')

                    res = stub.unlock(cargs[0], int(cargs[1]), args['client_id'])
                elif cmd == 'STATUS':
                    if len(cargs) < 1:
                        raise Exception('STATUS resource_id is required')

                    if not cargs[0].isdigit():
                        raise Exception('STATUS resource_id must be a digit')

                    res = stub.status(int(cargs[0]))
                elif cmd == 'STATS':
                    if len(cargs) < 1:
                        raise Exception('STATS subcommand is required')

                    scmd, *sargs = cargs

                    if scmd == 'K':
                        if len(sargs) < 1:
                            raise Exception('STATS resource_id is required')
                        elif len(sargs) > 1:
                            raise Exception('STATS too many arguments')

                        if not sargs[0].isdigit():
                            raise Exception('STATS resource_id must be a digit')

                        res = stub.stats_write_count(int(sargs[0]))
                    elif scmd == 'N':
                        if len(sargs) > 0:
                            raise Exception('STATS too many arguments')

                        res = stub.stats_unlocked()
                    elif scmd == 'D':
                        if len(sargs) > 0:
                            raise Exception('STATS too many arguments')

                        res = stub.stats_disabled()
                    else:
                        raise Exception('STATS subcommand must be K, N, or D')
                elif cmd == 'PRINT':
                    if len(cargs) > 0:
                        raise Exception('PRINT too many arguments')

                    res = stub.print()
                else:
                    raise Exception('UNKNOWN COMMAND')

                print(f'------\n  Pedido: {cmdinp}')
                print(f'Resposta: {", ".join(str(el) for el in res)}\n------')
            except Exception as e:
                print(e)
                # traceback.print_exc()
                continue
            finally:
                pass

        stub.disconnect()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
