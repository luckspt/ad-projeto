# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 1 - net_client.py
Grupo: 21
Números de aluno: 56895, 56926
"""

# zona para fazer importação
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

    def send_receive(self, data: str):
        """
        Envia os dados contidos em data para a socket da ligação, e retorna
        a resposta recebida pela mesma socket.
        """
        self.socket.sendall(data.encode('utf-8'))

        # TODO max length é 1024?
        msg = sock_utils.receive_all(self.socket, 1024)
        return msg.decode('utf-8')

    def close(self):
        """
        Termina a ligação ao servidor.
        """
        self.socket.close()
