#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_stub.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

from typing import List, Union
import net_client


class lock_stub:
    """
    Abstrai uma ligação a um servidor TCP. Implementa métodos para: estabelecer 
    a ligação; comandos existentes; terminar a ligação.
    """

    def __init__(self, address: str, port: int):
        """
        Inicializa a classe com parâmetros para funcionamento futuro.
        """
        self.client = net_client.server_connection(address, port)

    def connect(self):
        """
        Estabelece a ligação ao servidor especificado na inicialização.
        """
        self.client.connect()

    def disconnect(self):
        """
        Termina a ligação ao servidor.
        """
        self.client.close()

    def lock(self, type: str, resource_id: int, time_limit: int, client_id: int) -> List[int, Union[bool, None]]:
        """
        Prende um recurso no servidor.
        """
        return self.client.send_receive([10, type, resource_id, time_limit, client_id])

    def unlock(self, type: str, resource_id: int, client_id: int) -> List[int, Union[bool, None]]:
        """
        Liberta um recurso no servidor.
        """
        return self.client.send_receive([20, type, resource_id, client_id])

    def status(self, resource_id: int) -> List[int, Union[str, None]]:
        """
        Obtém o estado de um recurso no servidor.
        """
        return self.client.send_receive([30, resource_id])

    def stats_write_count(self, resource_id: int) -> List[int, Union[int, str, None]]:
        """
        Obtém quantas vezes um recurso foi preso.
        """
        return self.client.send_receive([40, resource_id])

    def stats_unlocked(self) -> List[int, Union[int, str, None]]:
        """
        Obtém quantos recursos estão libertos.
        """
        return self.client.send_receive([50])

    def stats_disabled(self) -> List[int, Union[int, str, None]]:
        """
        Obtém quantos recursos estão desabilitados.
        """
        return self.client.send_receive([60])

    def print(self) -> List[int, str]:
        """
        Obtém a lista de recursos com os seus estados e outras informações.
        """
        return self.client.send_receive([70])
