# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - sock_utils.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

import socket as s
from typing import Union


def create_tcp_server_socket(address, port, queue_size):
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    sock.bind((address, port))
    sock.listen(queue_size)
    return sock


def create_tcp_client_socket(address, port):
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    sock.connect((address, port))
    return sock


def receive_all(socket: s.socket, length: int) -> Union[bytearray, None]:
    data = bytearray()
    try:
        while len(data) < length:
            packet = socket.recv(length - len(data))
            if len(packet) == 0:
                break
            data.extend(packet)

        return data
    except:
        return None
