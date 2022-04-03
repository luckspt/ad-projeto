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

            # Empty line
            if not cmdinp:
                continue

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
                        if time_limit < 0:
                            raise Exception('SLEEP time_limit must be positive float')

                        sleep(time_limit)
                        continue
                    except ValueError:
                        raise Exception('SLEEP time_limit must be a float')
                    except KeyboardInterrupt:
                        continue
                    except:
                        raise Exception('SLEEP could not sleep :(')

                elif cmd == 'LOCK':
                    if len(cargs) < 3:
                        raise Exception('LOCK type, resource_id, and time_limit are required')
                    elif len(cargs) > 3:
                        raise Exception('LOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('LOCK type must be R or W')

                    if not cargs[1].isdigit() or int(cargs[1]) < 1:
                        raise Exception('LOCK resource_id must be a digit greater or equal to 1')

                    if not cargs[2].isdigit() or int(cargs[2]) < 0:
                        raise Exception('LOCK time_limit must be a positive digit')

                    res = stub.lock(cargs[0], int(cargs[1]), int(cargs[2]), args['client_id'])
                elif cmd == 'UNLOCK':
                    if len(cargs) < 2:
                        raise Exception('UNLOCK type and resource_id are required')
                    elif len(cargs) > 2:
                        raise Exception('UNLOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('UNLOCK type must be R or W')

                    if not cargs[1].isdigit() or int(cargs[1]) < 1:
                        raise Exception('UNLOCK resource_id must be a digit greater or equal to 1')

                    res = stub.unlock(cargs[0], int(cargs[1]), args['client_id'])
                elif cmd == 'STATUS':
                    if len(cargs) < 1:
                        raise Exception('STATUS resource_id is required')
                    elif len(cargs) > 1:
                        raise Exception('STATUS too many arguments')

                    if not cargs[0].isdigit() or int(cargs[0]) < 1:
                        raise Exception('STATUS resource_id must be a digit greater or equal to 1')

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

                        if not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception('STATS resource_id must be a digit greater or equal to 1')

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

                print(f'------\nPedido:\n{cmdinp}')
                print(f'Resposta:\n{", ".join(str(el) for el in res)}\n------')
            except ValueError:
                print('Could not convert a type, read the manual')
            except BrokenPipeError:
                print('Server connection lost, run the script again')
                break
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    except ConnectionRefusedError:
        print('Server connection refused, check address and port')
    except Exception as e:
        print('Error:', e)
    finally:
        stub.disconnect()

if __name__ == '__main__':
    main()
