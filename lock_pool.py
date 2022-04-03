#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 2 - lock_pool.py
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto
"""

from time import time
from functools import reduce
from typing import Union


class resource_lock:
    def __init__(self, resource_id: int):
        """
        Define e inicializa as propriedades do recurso para os bloqueios.
        """
        self.resource_id = resource_id
        self.write_lock = (None, 0)  # (client_id, deadline)
        self.read_lock = []  # (client_id, deadline)
        self.state = 'UNLOCKED'
        self.write_lock_count = 0

    def lock(self, type: str, client_id: int, time_limit: int) -> bool:
        """
        Tenta bloquear o recurso pelo cliente client_id, durante time_limit
        segundos. O bloqueio pode ser de escrita (type=W)
        ou de leitura (type=R).
        """
        if self.state == 'DISABLED':
            return False

        if type == 'W':
            if self.state == 'LOCKED-W' or self.state == 'LOCKED-R':
                return False
            else:
                self.state = 'LOCKED-W'
                deadline = time() + time_limit
                self.write_lock = (client_id, deadline)
                self.write_lock_count += 1
                return True
        else:  # type == 'R'
            if self.state == 'LOCKED-W':
                return False
            else:
                self.state = 'LOCKED-R'
                deadline = time() + time_limit
                self.read_lock.append((client_id, deadline))
                return True

    def release(self):
        """
        Liberta o recurso incondicionalmente, alterando os valores associados
        ao bloqueio.
        """
        self.write_lock = (None, 0)
        self.read_lock = []
        self.state = 'UNLOCKED'

    def unlock(self, type: str, client_id: int) -> bool:
        """
        Liberta o recurso se este está bloqueado pelo cliente client_id.
        O desbloqueio pode ser relacionado a bloqueios
        de escrita (type=W) ou de leitura (type=R), consoante o tipo.
        """
        if self.state == 'DISABLED' or self.state == 'UNLOCKED':
            return False

        if type == 'W':
            if self.state == 'LOCKED-W' and self.write_lock[0] != client_id:
                return False

            self.write_lock = (None, 0)
            self.state = 'UNLOCKED'

            return True
        else:  # type == 'R'
            if self.state == 'LOCKED-R':
                ok = False
                for i, concessao in enumerate(self.read_lock):
                    if concessao[0] == client_id:
                        self.read_lock.pop(i)
                        ok = True  # Ups! não estava na entrega 1

                if len(self.read_lock) == 0:
                    self.state = 'UNLOCKED'

                if ok:
                    return True

        # Se o cliente não tiver lock no recurso
        return False

    def status(self) -> str:
        """
        Obtém o estado do recurso. Retorna LOCKED-W ou LOCKED-R ou UNLOCKED,
        ou DISABLED.
        """
        return self.state

    def stats(self) -> int:
        """
        Retorna o número de bloqueios de escrita feitos neste recurso.
        """
        return self.write_lock_count

    def disable(self):
        """
        Coloca o recurso como desabilitado incondicionalmente, alterando os
        valores associados à sua disponibilidade.
        """
        self.write_lock = (None, 0)
        self.read_lock = []
        self.state = 'DISABLED'

    def __repr__(self) -> str:
        """
        Representação da classe para a saída standard. A string devolvida por
        esta função é usada, por exemplo, se uma instância da classe for
        passada à função print ou str.
        """
        output = f'{self.state} {self.write_lock_count}'

        if self.state == 'LOCKED-W':
            output += f' {self.write_lock[0]} {self.write_lock[1]}'
        elif self.state == 'LOCKED-R':
            qtd_clientes = len(set(map(lambda c: c[0], self.read_lock)))
            max_concessao = reduce(lambda acc, c: acc if acc > c[1] else c[1]
                                   , self.read_lock
                                   , 0)  # (client_id, deadline)
            output += f' {qtd_clientes} {max_concessao}'

        return output


###############################################################################

class lock_pool:
    def __init__(self, n: int, k: int):
        """
        Define um array com um conjunto de resource_locks para N recursos.
        Os locks podem ser manipulados pelos métodos desta classe.
        Define K, o número máximo de bloqueios de escrita permitidos para cada
        recurso. Ao atingir K bloqueios de escrita, o recurso fica desabilitado.
        """
        self.resources = [resource_lock(i) for i in range(n)]
        self.max_resource_locks = k

    def clear_expired_locks(self):
        """
        Verifica se os recursos que estão bloqueados ainda estão dentro do tempo
        de concessão dos bloqueios. Remove os bloqueios para os quais o tempo de
        concessão tenha expirado.
        """
        for resource in self.resources:
            now = time()
            if resource.status() == 'LOCKED-W':
                if resource.write_lock[1] != 0 and resource.write_lock[1] < now:
                    if resource.stats() >= self.max_resource_locks:
                        resource.disable()
                    else:
                        resource.release()
            elif resource.status() == 'LOCKED-R':
                if all(t[1] < now for t in resource.read_lock):
                    resource.release()

    def lock(self, type: str, resource_id: int, client_id: int, time_limit: int) -> Union[bool, None]:
        """
        Tenta bloquear (do tipo R ou W) o recurso resource_id pelo cliente client_id,
        durante time_limit segundos. Retorna True, False ou None.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return None

        resource = self.resources[resource_id - 1]
        if type == 'W' and resource.stats() >= self.max_resource_locks:
            return False

        return resource.lock(type, client_id, time_limit)

    def unlock(self, type: str, resource_id: int, client_id: int) -> Union[bool, None]:
        """
        Liberta o bloqueio (do tipo R ou W) sobre o recurso resource_id pelo cliente
        client_id. Retorna True, False ou None.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return None

        resource = self.resources[resource_id - 1]

        res = resource.unlock(type, client_id)
        if resource.stats() >= self.max_resource_locks:
            resource.disable()

        return res

    def status(self, resource_id: int) -> Union[str, None]:
        """
        Obtém o estado de um recurso. Retorna LOCKED, UNLOCKED,
        DISABLED ou None.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return None

        resource = self.resources[resource_id - 1]

        return resource.status()

    def stats(self, option: str, resource_id: Union[int, None]) -> Union[int, str, None]:
        """
        Obtém o estado do serviço de gestão de bloqueios. Se option for K, retorna <número de
        bloqueios feitos no recurso resource_id> ou None. Se option for N, retorna
        <número de recursos bloqueados atualmente>. Se option for D, retorna
        <número de recursos desabilitados>
        """
        if option == 'K':
            if resource_id < 1 or resource_id > len(self.resources):
                return None

            resource = self.resources[resource_id - 1]

            return resource.stats()
        elif option == 'N':
            return reduce(lambda acc, r: acc + int(r.status() == 'UNLOCKED'), self.resources, 0)
        elif option == 'D':
            return reduce(lambda acc, r: acc + int(r.status() == 'DISABLED'), self.resources, 0)
        else:
            return None

    def __repr__(self) -> str:
        """
        Representação da classe para a saída standard. A string devolvida por
        esta função é usada, por exemplo, se uma instância da classe for
        passada à função print ou str.
        """
        return '\n'.join(
            map(lambda r: f'R {r[0] + 1} {r[1]}', enumerate(self.resources))
        )
