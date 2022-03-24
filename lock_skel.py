#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_skel.py
Grupo: 21
Números de aluno: 56895, 56926
"""

import pickle
from lock_pool import lock_pool


class lock_skel:
    def __init__(self, n, k):
        self.servicoLista = []
        self.lp = lock_pool(n, k)

    def processMessage(self, msg_bytes):
        # recebe bytes e desserializa o pedido
        pedido = self.bytesToList(msg_bytes)

        print(f'------\n  Pedido: {", ".join(str(el) for el in pedido)}')
        try:
            cmd, *cargs = pedido

            res = [pedido[0] + 1]

            self.lp.clear_expired_locks()
            if cmd == 10:
                if len(cargs) < 4:
                    raise Exception('LOCK type, resource_id, time_limit, and client_id are required')
                elif len(cargs) > 4:
                    raise Exception('LOCK too many arguments')

                if cargs[0] not in {'R', 'W'}:
                    raise Exception('LOCK type must be R or W')

                if not isinstance(cargs[1], int):
                    raise Exception('LOCK resource_id must be an int')

                if not isinstance(cargs[2], int):
                    raise Exception('LOCK time_limit must be an int')

                if not isinstance(cargs[3], int):
                    raise Exception('LOCK client_id must be an int')

                resp = self.lp.lock(cargs[0], cargs[1], cargs[3], cargs[2])
                res.append(resp)
            elif cmd == 20:
                if len(cargs) < 3:
                    raise Exception('UNLOCK type, resource_id, and client_id are required')
                elif len(cargs) > 3:
                    raise Exception('UNLOCK too many arguments')

                if cargs[0] not in {'R', 'W'}:
                    raise Exception('UNLOCK type must be R or W')

                if not isinstance(cargs[1], int):
                    raise Exception('UNLOCK resource_id must be an int')

                if not isinstance(cargs[2], int):
                    raise Exception('UNLOCK client_id must be an int')

                resp = self.lp.unlock(cargs[0], cargs[1], cargs[2])
                res.append(resp)
            elif cmd == 30:
                if len(cargs) < 1:
                    raise Exception('STATUS resource_id is required')

                resp = self.lp.status(cargs[0])
                res.append(resp)
            elif cmd == 40:
                if len(cargs) < 1:
                    raise Exception('STATS resource_id is required')
                elif len(cargs) > 1:
                    raise Exception('STATS too many arguments')

                resp = self.lp.stats('K', cargs[0])
                res.append(resp)
            elif cmd == 50:
                if len(cargs) > 1:
                    raise Exception('STATS too many arguments')

                resp = self.lp.stats('N', None)
                res.append(resp)
            elif cmd == 60:
                if len(cargs) > 1:
                    raise Exception('STATS too many arguments')

                resp = self.lp.stats('D', None)
                res.append(resp)
            elif cmd == 70:
                res.append(str(self.lp))
            else:
                raise Exception('UNKNOWN COMMAND')
        except Exception as e:
            res.append(str(e))

        print(f'Resposta: {", ".join(str(el) for el in res)}\n------')
        return self.listToBytes(res)

    def bytesToList(self, msg_bytes):
        return pickle.loads(msg_bytes)

    def listToBytes(self, resposta):
        return pickle.dumps(resposta)



