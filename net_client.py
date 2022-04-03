# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - net_client.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

# zona para fazer importação
import pickle
import struct
from typing import Any

import sock_utils
import socket as s


# definição da classe server_connection

class server_connection:
    """
    Abstrai uma ligação a um servidor TCP. Implementa métodos para: estabelecer 
    a ligação; envio de um comando e receção da resposta; terminar a ligação.
    """

    def __init__(self, address: str, port: int):
        """
        Inicializa a classe com parâmetros para funcionamento futuro.
        """
        self.address = address
        self.port = port
        self.socket: s.socket = None

    def connect(self):
        """
        Estabelece a ligação ao servidor especificado na inicialização.
        """
        self.socket = sock_utils.create_tcp_client_socket(self.address, self.port)

    def send_receive(self, data: Any) -> Any:
        """
        Envia os dados contidos em data para a socket da ligação, e retorna
        a resposta recebida pela mesma socket.
        """
        # Serialize
        msg_bytes = pickle.dumps(data, -1)
        size_bytes = struct.pack('i', len(msg_bytes))

        # Send
        self.socket.sendall(size_bytes)
        self.socket.sendall(msg_bytes)

        # Receive
        req_size_bytes = sock_utils.receive_all(self.socket, 4)
        size = struct.unpack('i', req_size_bytes)[0]

        # Deserialize
        req_bytes = sock_utils.receive_all(self.socket, size)
        res = pickle.loads(req_bytes)

        return res

    def close(self):
        """
        Termina a ligação ao servidor.
        """
        self.socket.close()
