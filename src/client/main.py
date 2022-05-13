#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 4 - client/main.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer imports
from argparse import ArgumentParser
from typing import Dict, Union, Tuple
import requests
import json
from reqs import Reqs
from playlists import Playlists
import urllib3

# Desativar avisos do SubjectAltNameWarning
urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)


# Programa principal
AVALIACOES = {'M', 'm', 'S', 'B', 'MB'}


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


def main() -> None:
    """
    Programa principal
    """
    args = parse()

    try:
        base_url = f'https://{args["address"]}:{args["port"]}'
        api = Playlists(Reqs(base_url, '../certs/root.pem',
                        ('../certs/cli.crt', '../certs/cli.key')))

        while True:
            try:
                cmdinp = input('comando > ')

                # Empty line
                if not cmdinp:
                    continue

                cmd, *cargs = cmdinp.split()

                res = None
                if not cmd:
                    raise Exception('unknown command')
                elif cmd == 'EXIT':
                    break
                elif cmd == 'CREATE':
                    if not cargs:
                        raise Exception('CREATE missing subcommand')
                    scmd, *sargs = cargs

                    if scmd == 'UTILIZADOR':
                        if len(sargs) < 2:
                            raise Exception(
                                'CREATE UTILIZADOR nome and senha are required')
                        elif len(sargs) > 2:
                            raise Exception(
                                'CREATE UTILIZADOR too many arguments')

                        res = api.create_user(*sargs)

                    elif scmd == 'ARTISTA':
                        if len(sargs) < 1:
                            raise Exception(
                                'CREATE ARTISTA id_spotify is required')
                        elif len(sargs) > 1:
                            raise Exception(
                                'CREATE ARTISTA too many arguments')

                        res = api.create_artist(*sargs)

                    elif scmd == 'MUSICA':
                        if len(sargs) < 1:
                            raise Exception(
                                'CREATE MUSICA id_spotify is required')
                        elif len(sargs) > 1:
                            raise Exception('CREATE MUSICA too many arguments')

                        res = api.create_music(*sargs)

                    else:
                        if len(cargs) < 3:
                            raise Exception(
                                'CREATE id_user, id_musica, and avaliacao are required')
                        elif len(cargs) > 3:
                            raise Exception('CREATE too many arguments')
                        elif not cargs[0].isdigit() or int(cargs[0]) < 1:
                            raise Exception(
                                'CREATE id_utilizador must be a digit greater or equal to 1')
                        elif not cargs[1].isdigit() or int(cargs[1]) < 1:
                            raise Exception(
                                'CREATE id_musica must be a digit greater or equal to 1')
                        elif cargs[2] not in AVALIACOES:
                            raise Exception(
                                f'CREATE avaliacao type must be one of {", ".join(AVALIACOES)}')

                        res = api.create_user_rating(*cargs)

                elif cmd == 'READ':
                    if not cargs:
                        raise Exception('READ missing subcommand')
                    scmd, *sargs = cargs

                    if scmd == 'UTILIZADOR':
                        if len(sargs) < 1:
                            raise Exception(
                                'READ UTILIZADOR id_utilizador is required')
                        elif len(sargs) > 1:
                            raise Exception(
                                'READ UTILIZADOR too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'READ UTILIZADOR id_utilizador must be a digit greater or equal to 1')

                        res = api.get_user(*sargs)

                    elif scmd == 'ARTISTA':
                        if len(sargs) < 1:
                            raise Exception(
                                'READ ARTISTA id_artista is required')
                        elif len(sargs) > 1:
                            raise Exception('READ ARTISTA too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'READ ARTISTA id_artista must be a digit greater or equal to 1')

                        res = api.get_artist(*sargs)

                    elif scmd == 'MUSICA':
                        if len(sargs) < 1:
                            raise Exception(
                                'READ MUSICA id_musica is required')
                        elif len(sargs) > 1:
                            raise Exception('READ MUSICA too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'READ MUSICA id_musica must be a digit greater or equal to 1')

                        res = api.get_music(*sargs)

                    elif scmd == 'ALL':
                        if not sargs:
                            raise Exception('READ ALL missing subcommand')
                        sscmd, *ssargs = sargs

                        if sscmd == 'UTILIZADORES':
                            res = api.get_all_users()
                        elif sscmd == 'ARTISTAS':
                            res = api.get_all_artists()
                        elif sscmd == 'MUSICAS':
                            if len(ssargs) == 0:
                                res = api.get_all_musics()
                            elif len(ssargs) == 1:
                                # ALL MUSICAS <avaliacao>
                                if ssargs[0] not in AVALIACOES:
                                    raise Exception(
                                        f'READ ALL MUSICAS avaliacao type must be one of {", ".join(AVALIACOES)}')

                                res = api.get_all_musics(*ssargs)
                            else:
                                raise Exception(
                                    'READ ALL MUSICAS too many arguments')
                        elif sscmd == 'MUSICAS_A':
                            if len(ssargs) < 1:
                                raise Exception(
                                    'READ ALL MUSICAS_A id_artista is required')
                            elif len(ssargs) > 1:
                                raise Exception(
                                    'READ ALL MUSICAS_A too many arguments')
                            elif not ssargs[0].isdigit() or int(ssargs[0]) < 1:
                                raise Exception(
                                    'READ ALL MUSICAS_A id_artista must be a digit greater or equal to 1')

                            res = api.get_all_musics_artist(*ssargs)
                        elif sscmd == 'MUSICAS_U':
                            if len(ssargs) < 1:
                                raise Exception(
                                    'READ ALL MUSICAS_U id_utilizador is required')
                            elif len(ssargs) > 1:
                                raise Exception(
                                    'READ ALL MUSICAS_U too many arguments')
                            elif not ssargs[0].isdigit() or int(ssargs[0]) < 1:
                                raise Exception(
                                    'READ ALL MUSICAS_U id_utilizador must be a digit greater or equal to 1')

                            res = api.get_all_musics_user(*ssargs)
                        else:
                            raise Exception('READ ALL unknown command')
                    else:
                        raise Exception('READ unknown command')
                elif cmd == 'DELETE':
                    if not cargs:
                        raise Exception('DELETE missing subcommand')
                    scmd, *sargs = cargs

                    if scmd == 'UTILIZADOR':
                        if len(sargs) < 1:
                            raise Exception(
                                'DELETE UTILIZADOR id_utilizador is required')
                        elif len(sargs) > 1:
                            raise Exception(
                                'DELETE UTILIZADOR too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'DELETE UTILIZADOR id_utilizador must be a digit greater or equal to 1')

                        res = api.delete_user(*sargs)

                    elif scmd == 'ARTISTA':
                        if len(sargs) < 1:
                            raise Exception(
                                'DELETE ARTISTA id_artista is required')
                        elif len(sargs) > 1:
                            raise Exception(
                                'DELETE ARTISTA too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'DELETE ARTISTA id_artista must be a digit greater or equal to 1')

                        res = api.delete_artist(*sargs)

                    elif scmd == 'MUSICA':
                        if len(sargs) < 1:
                            raise Exception(
                                'DELETE MUSICA id_musica is required')
                        elif len(sargs) > 1:
                            raise Exception('DELETE MUSICA too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'DELETE MUSICA id_musica must be a digit greater or equal to 1')

                        res = api.delete_music(*sargs)

                    elif scmd == 'ALL':
                        if not sargs:
                            raise Exception('DELETE ALL missing subcommand')
                        sscmd, *ssargs = sargs

                        if sscmd == 'UTILIZADORES':
                            res = api.delete_all_users()
                        elif sscmd == 'ARTISTAS':
                            res = api.delete_all_artists()
                        elif sscmd == 'MUSICAS':
                            if len(ssargs) == 0:
                                res = api.delete_all_musics()
                            elif len(ssargs) == 1:
                                # ALL MUSICAS <avaliacao>
                                if ssargs[0] not in AVALIACOES:
                                    raise Exception(
                                        f'DELETE ALL MUSICAS avaliacao type must be one of {", ".join(AVALIACOES)}')

                                res = api.delete_all_musics(*ssargs)
                            else:
                                raise Exception(
                                    'DELETE ALL MUSICAS too many arguments')
                        elif sscmd == 'MUSICAS_A':
                            if len(ssargs) < 1:
                                raise Exception(
                                    'DELETE ALL MUSICAS_A id_artista is required')
                            elif len(ssargs) > 1:
                                raise Exception(
                                    'DELETE ALL MUSICAS_A too many arguments')
                            elif not ssargs[0].isdigit() or int(ssargs[0]) < 1:
                                raise Exception(
                                    'DELETE ALL MUSICAS_A id_artista must be a digit greater or equal to 1')

                            res = api.delete_all_musics_artist(*ssargs)
                        elif sscmd == 'MUSICAS_U':
                            if len(ssargs) < 1:
                                raise Exception(
                                    'DELETE ALL MUSICAS_U id_utilizador is required')
                            elif len(ssargs) > 1:
                                raise Exception(
                                    'DELETE ALL MUSICAS_U too many arguments')
                            elif not ssargs[0].isdigit() or int(ssargs[0]) < 1:
                                raise Exception(
                                    'DELETE ALL MUSICAS_U id_utilizador must be a digit greater or equal to 1')

                            res = api.delete_all_musics_user(*ssargs)
                        else:
                            raise Exception('DELETE ALL unknown command')
                    else:
                        raise Exception('DELETE unknown command')

                elif cmd == 'UPDATE':
                    if not cargs:
                        raise Exception('UPDATE missing subcommand')
                    scmd, *sargs = cargs
                    if scmd == 'MUSICA':
                        if len(sargs) < 3:
                            raise Exception(
                                'UPDATE MUSICA id_musica, avaliacao, id_utilizador are required')
                        elif len(sargs) > 3:
                            raise Exception('UPDATE MUSICA too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'UPDATE MUSICA id_musica must be a digit greater or equal to 1')
                        elif sargs[1] not in AVALIACOES:
                            raise Exception(
                                f'UPDATE MUSICA avaliacao type must be one of {", ".join(AVALIACOES)}')
                        elif not sargs[2].isdigit() or int(sargs[2]) < 1:
                            raise Exception(
                                'UPDATE MUSICA id_utilizador must be a digit greater or equal to 1')

                        res = api.update_music(*sargs)
                    elif scmd == 'UTILIZADOR':
                        if len(sargs) < 2:
                            raise Exception(
                                'UPDATE UTILIZADOR id_utilizador, password are required')
                        elif len(sargs) > 2:
                            raise Exception(
                                'UPDATE UTILIZADOR too many arguments')
                        elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                            raise Exception(
                                'UPDATE UTILIZADOR id_utilizador must be a digit greater or equal to 1')

                        res = api.update_user(*sargs)
                    else:
                        raise Exception('UPDATE unknown command')
                else:
                    raise Exception('unknown command')

                if res:
                    print(json.dumps(res, sort_keys=True,
                          indent=4, ensure_ascii=False))
            except ValueError:
                print('Could not convert a type, read the manual')
            except requests.exceptions.HTTPError as e:
                print('HTTP error:', e)
            except requests.exceptions.ConnectionError:
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
