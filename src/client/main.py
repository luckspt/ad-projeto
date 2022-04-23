#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 3 - client/main.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# Zona para fazer imports
from argparse import ArgumentParser
import json
from typing import Dict, Union, Tuple
from api import Api

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
    try:
        args = parse()

        base_url = f'http://{args["address"]}:{args["port"]}'
        api = Api(base_url)

        res = None

        while True:
            cmdinp = input('comando > ')

            # Empty line
            if not cmdinp:
                continue

            cmd, *cargs = cmdinp.split()

            if len(cmd) == 0:
                raise Exception('unknown command')
            elif cmd == 'EXIT':
                break
            elif cmd == 'CREATE':
                scmd, *sargs = cargs

                if scmd == 'UTILIZADOR':
                    if len(sargs) < 2:
                        raise Exception(
                            'CREATE UTILIZADOR nome and senha are required')
                    elif len(sargs) > 2:
                        raise Exception('CREATE UTILIZADOR too many arguments')

                    dados = {
                        'nome': sargs[0],
                        'senha': sargs[1]
                    }

                    res = api.post('/utilizadores', dados)
                    # TODO trabalhar a resposta
                elif scmd == 'ARTISTA':
                    if len(sargs) < 1:
                        raise Exception(
                            'CREATE ARTISTA id_spotify is required')
                    elif len(cargs) > 1:
                        raise Exception('CREATE ARTISTA too many arguments')

                    dados = {
                        'id_spotify': sargs[0]
                    }

                    res = api.post('/artistas', dados)
                    # TODO trabalhar a resposta
                elif scmd == 'MUSICA':
                    if len(sargs) < 1:
                        raise Exception('CREATE MUSICA id_spotify is required')
                    elif len(sargs) > 1:
                        raise Exception('CREATE MUSICA too many arguments')

                    dados = {
                        'id_spotify': sargs[0]
                    }

                    res = api.post('/musicas', dados)
                    # TODO trabalhar a resposta
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

                    dados = {
                        'id_utilizador': cargs[0],
                        'id_musica': cargs[1],
                        'avaliacao': cargs[2]
                    }

                    # TODO definir rota
                    res = api.post('/todo', dados)
                    # TODO trabalhar a resposta

            elif cmd == 'READ':
                scmd, *sargs = cargs

                if scmd == 'UTILIZADOR':
                    if len(sargs) < 1:
                        raise Exception(
                            'READ UTILIZADOR id_utilizador is required')
                    elif len(sargs) > 1:
                        raise Exception('READ UTILIZADOR too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'READ UTILIZADOR id_utilizador must be a digit greater or equal to 1')

                    res = api.get(f'/utilizadores/{sargs[0]}')
                    # TODO trabalhar a resposta

                elif scmd == 'ARTISTA':
                    if len(sargs) < 1:
                        raise Exception('READ ARTISTA id_artista is required')
                    elif len(sargs) > 1:
                        raise Exception('READ ARTISTA too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'READ ARTISTA id_artista must be a digit greater or equal to 1')

                    res = api.get(f'/artistas/{sargs[0]}')
                    # TODO trabalhar a resposta

                elif scmd == 'MUSICA':
                    if len(sargs) < 1:
                        raise Exception('READ MUSICA id_musica is required')
                    elif len(sargs) > 1:
                        raise Exception('READ MUSICA too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'READ MUSICA id_musica must be a digit greater or equal to 1')

                    res = api.get(f'/musicas/{sargs[0]}')
                    # TODO trabalhar a resposta

                elif scmd == 'ALL':
                    sscmd, *ssargs = sargs

                    if sscmd == 'UTILIZADORES':
                        res = api.get('/utilizadores')
                        # TODO trabalhar a resposta
                    elif sscmd == 'ARTISTAS':
                        res = api.get('/artistas')
                        # TODO trabalhar a resposta
                    elif sscmd == 'MUSICAS':
                        if len(ssargs) == 0:
                            res = api.get('/musicas')
                            # TODO trabalhar a resposta
                        elif len(ssargs) == 1:
                            # ALL MUSICAS <avaliacao>
                            if ssargs[0] not in AVALIACOES:
                                raise Exception(
                                    f'READ ALL MUSICAS avaliacao type must be one of {", ".join(AVALIACOES)}')

                            params = {
                                'avaliacao': ssargs[0]
                            }
                            res = api.get('/musicas', params)
                            # TODO trabalhar a resposta~
                        else:
                            pass
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

                        params = {
                            'id_artista': ssargs[0]
                        }
                        res = api.get('/musicas', params)
                        # TODO trabalhar a resposta
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

                        params = {
                            'id_artista': ssargs[0]
                        }
                        res = api.get('/musicas', params)
                        # TODO trabalhar a resposta
                    else:
                        raise Exception('READ ALL unknown command')
                else:
                    raise Exception('READ unknown command')
            elif cmd == 'DELETE':
                scmd, *sargs = cargs

                if scmd == 'UTILIZADOR':
                    if len(sargs) < 1:
                        raise Exception(
                            'DELETE UTILIZADOR id_utilizador is required')
                    elif len(sargs) > 1:
                        raise Exception('DELETE UTILIZADOR too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'DELETE UTILIZADOR id_utilizador must be a digit greater or equal to 1')

                    res = api.delete(f'/utilizadores/{sargs[0]}')
                    # TODO trabalhar a resposta

                elif scmd == 'ARTISTA':
                    if len(sargs) < 1:
                        raise Exception(
                            'DELETE ARTISTA id_artista is required')
                    elif len(sargs) > 1:
                        raise Exception('DELETE ARTISTA too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'DELETE ARTISTA id_artista must be a digit greater or equal to 1')

                    res = api.delete(f'/artistas/{sargs[0]}')
                    # TODO trabalhar a resposta

                elif scmd == 'MUSICA':
                    if len(sargs) < 1:
                        raise Exception('DELETE MUSICA id_musica is required')
                    elif len(sargs) > 1:
                        raise Exception('DELETE MUSICA too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'DELETE MUSICA id_musica must be a digit greater or equal to 1')

                    res = api.delete(f'/musicas/{sargs[0]}')
                    # TODO trabalhar a resposta

                elif scmd == 'ALL':
                    sscmd, *ssargs = sargs

                    if sscmd == 'UTILIZADORES':
                        res = api.delete('/utilizadores')
                        # TODO trabalhar a resposta
                    elif sscmd == 'ARTISTAS':
                        res = api.delete('/artistas')
                        # TODO trabalhar a resposta
                    elif sscmd == 'MUSICAS':
                        if len(ssargs) == 0:
                            res = api.delete('/musicas')
                            # TODO trabalhar a resposta
                        elif len(ssargs) == 1:
                            # ALL MUSICAS <avaliacao>
                            if ssargs[0] not in AVALIACOES:
                                raise Exception(
                                    f'DELETE ALL MUSICAS avaliacao type must be one of {", ".join(AVALIACOES)}')

                            res = api.delete(f'/musicas?avaliacao={ssargs[0]}')
                            # TODO trabalhar a resposta~
                        else:
                            pass
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

                        res = api.delete(f'/musicas?id_artista={ssargs[0]}')
                        # TODO trabalhar a resposta
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

                        res = api.delete(f'/musicas?id_artista={ssargs[0]}')
                        # TODO trabalhar a resposta
                    else:
                        raise Exception('DELETE ALL unknown command')
                else:
                    raise Exception('DELETE unknown command')

            elif cmd == 'UPDATE':
                scmd, *sargs = cargs
                if scmd == 'MUSICA':
                    # TODO perguntar ao prof o que é atualizar uma música??? atualizar com que dados???
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

                    dados = {
                        'id_musica': sargs[0],
                        'avaliacao': sargs[1],
                        'id_utilizador': sargs[2]
                    }

                    res = api.put('/todo', dados)
                    # TODO trabalhar a resposta

                elif scmd == 'UTILIZADOR':
                    if len(sargs) < 2:
                        raise Exception(
                            'UPDATE UTILIZADOR id_utilizador, password are required')
                    elif len(sargs) > 2:
                        raise Exception('UPDATE UTILIZADOR too many arguments')
                    elif not sargs[0].isdigit() or int(sargs[0]) < 1:
                        raise Exception(
                            'UPDATE UTILIZADOR id_utilizador must be a digit greater or equal to 1')

                    dados = {
                        'password': sargs[1]
                    }

                    res = api.put('/utilizadores', dados)
                    # TODO trabalhar a resposta
                else:
                    raise Exception('UPDATE unknown command')

            print(json.dumps(res, sort_keys=True, indent=4, ensure_ascii=False))
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
