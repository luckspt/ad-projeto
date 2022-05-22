#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 4 - client/maindict.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer imports
from argparse import ArgumentParser
import json
from typing import Callable, Dict, List, Union, Tuple
import requests
from reqs import Reqs
from playlists import Playlists
import urllib3

# Desativar avisos do SubjectAltNameWarning
urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)


# Programa principal
def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(
        description='Cliente da API Flask do Serviço de Playlists')

    parser.add_argument(
        "address",
        help="IP ou Hostname do Servidor que fornece os recursos",
        default='localhost'
    )

    parser.add_argument(
        "port",
        help="Porto TCP do Servidor que fornece os recursos",
        type=int,
        default=9999
    )

    args = parser.parse_args().__dict__

    return args


def int_cmd_args(args):
    return len(args) == 1 and args[0].isdigit()


AVALIACOES = {'M', 'm', 'S', 'B', 'MB'}


def resolve_command(dic: Dict[str, Tuple[Callable, Callable]], command: str, args: List[str] = None) -> Tuple[Callable, List[str]]:
    """
    Resolve um comando recebido do utilizador.
    :param command: Comando a ser executado.
    :param dic: Dict com os comandos disponíveis.
    :param args: Dict com valores dos argumentos escolhidos pelo utilizador.
    :return: None
    """
    if args is None:
        args = []

    c = command.upper()
    if c in dic:
        if isinstance(dic[c], dict):
            # Has subcommands
            command = args.pop(0)
            return resolve_command(dic[c], command, args)
        elif isinstance(dic[c], tuple):
            # Is a command with arg filters
            if dic[c][0](args):
                return dic[c][1], args
            else:
                raise Exception(f'Invalid arguments for command {c}')
        elif isinstance(dic[c], Callable):
            # Is a command without arg filters
            return dic[c], args
        else:
            raise Exception('Unknown command')
    else:
        raise Exception('Unknown command')


def main() -> None:
    """
    Programa principal
    """
    # args = parse()
    prog_args = {
        'address': 'localhost',
        'port': 9000,
    }

    try:
        base_url = f'http://{prog_args["address"]}:{prog_args["port"]}'
        api = Playlists(Reqs(base_url, '../certs/root.pem',
                        ('../certs/cli.crt', '../certs/cli.key')))

        commands = {
            'EXIT': exit,
            'CREATE': {
                'UTILIZADOR': (lambda args: len(args) == 2, api.create_user),
                'ARTISTA': (lambda args: len(args) == 1, api.create_artist),
                'MUSICA': (lambda args: len(args) == 1, api.create_music),
            },
            'READ': {
                'UTILIZADOR': (int_cmd_args, api.get_user),
                'ARTISTA': (int_cmd_args, api.get_artist),
                'MUSICA': (int_cmd_args, api.get_music),
                'ALL': {
                    'UTILIZADORES': api.get_all_users,
                    'ARTISTAS': api.get_all_artists,
                    'MUSICAS': (
                        lambda args: len(args) == 0 or (len(args) == 1 and args[0] in AVALIACOES), api.get_all_musics),
                    'MUSICAS_A': (int_cmd_args, api.get_all_musics_artist),
                    'MUSICAS_U': (int_cmd_args, api.get_all_musics_user),
                },
            },
            'DELETE': {
                'UTILIZADOR': (int_cmd_args, api.delete_user),
                'ARTISTA': (int_cmd_args, api.delete_artist),
                'MUSICA': (int_cmd_args, api.delete_music),
                'ALL': {
                    'UTILIZADORES': api.delete_all_users,
                    'ARTISTAS': api.delete_all_artists,
                    'MUSICAS': (
                        lambda args: len(args) == 0 or (len(args) == 1 and args[0] in AVALIACOES), api.delete_all_musics),
                    'MUSICAS_A': (int_cmd_args, api.delete_all_musics_artist),
                    'MUSICAS_U': (int_cmd_args, api.delete_all_musics_user),
                },
            },
            'UPDATE': {
                'MUSICA': (lambda args: len(args) == 3 and args[0].isdigit() and args[1] in AVALIACOES and args[2].isdigit(),
                           api.update_music),
                'UTILIZADOR': (lambda args: len(args) == 2 and args[0].isdigit(), api.update_user),
            }
        }

        while True:
            try:
                cmdinp = input('comando > ')

                # Empty line
                if not cmdinp:
                    continue

                cmd, *cargs = cmdinp.split()
                res = None

                # Handle "CREATE <id_user> <id_musica> <avaliacao>" special case
                if cmd == 'CREATE' and len(cargs) == 3 and cargs[0] != 'UTILIZADOR':
                    if not cargs[0].isdigit() or not cargs[1].isdigit() or not cargs[2] in AVALIACOES:
                        raise Exception(
                            'Invalid arguments for command CREATE UTILIZADOR')

                    res = api.create_user_rating(*cargs)
                else:
                    command = resolve_command(commands, cmd, cargs)
                    if not command:
                        raise Exception('unknown command')
                    else:
                        f, args = command
                        res = f(*args)

                if res:
                    print(json.dumps(res, sort_keys=True,
                                     indent=4, ensure_ascii=False))
            except ValueError:
                print('Could not convert a type, read the manual')
            except requests.exceptions.HTTPError as e:
                print('HTTP error:', e)
            except requests.exceptions.ConnectionError as e:
                print('Could not connect to API')
            except requests.exceptions.Timeout as e:
                print('API Timeout:', e)
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


if __name__ == '__main__':
    main()
