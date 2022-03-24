#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_stub.py
Grupo: 21
Números de aluno: 56895, 56926
"""
from collections.abc import Iterable
from typing import Union, Any

import net_client


class lock_stub:
    def __init__(self, address: str, port: int):
        self.client = net_client.server_connection(address, port)

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.close()

    def send(self, cmd: int, data: Union[Iterable, Any] = None):
        parsed = [cmd]

        if data is not None:
            if isinstance(data, Iterable):
                parsed.extend(data)
            else:
                parsed.append(data)

        res = self.client.send_receive(parsed)
        return res

    def lock(self, type: str, resource_id: int, time_limit: int, client_id: int):
        return self.send(10, [type, resource_id, time_limit, client_id])

    def unlock(self, type: str, resource_id: int, client_id: int):
        return self.send(20, [type, resource_id, client_id])

    def status(self, resource_id: int):
        return self.send(30, [resource_id])

    def stats_write_count(self, resource_id: int):
        return self.send(40, resource_id)

    def stats_unlocked(self):
        return self.send(50)

    def stats_disabled(self):
        return self.send(60)

    def print(self):
        return self.send(70)
