#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 1 - lock_server.py
Grupo:
Números de aluno:
"""

# Zona para fazer importação
from argparse import ArgumentParser
from time import time
from functools import reduce
from typing import Dict, Union, Tuple


###############################################################################
import sock_utils


class resource_lock:
    def __init__(self, resource_id: int):
        """
        Define e inicializa as propriedades do recurso para os bloqueios.
        """
        self.resource_id = resource_id
        self.write_lock = (None, 0)  # (client_id, deadline)
        self.read_lock = {}
        self.state = None
        self.write_lock_count = 0

    # ainda nao esta ok LISTA
    def lock(self, type: str, client_id: str, time_limit: int):
        """
        Tenta bloquear o recurso pelo cliente client_id, durante time_limit 
        segundos. Retorna OK ou NOK. O bloqueio pode ser de escrita (type=W)
        ou de leitura (type=R).
        """
        if self.state == 'DISABLED':
            return 'NOK'

        if type == 'W':
            if self.state == 'LOCKED-W' or self.state == 'LOCKED-R':
                return 'NOK'
            else:
                self.state = 'LOCKED-W'
                deadline = time() + time_limit
                self.write_lock = (client_id, deadline)
                self.write_lock_count += 1
                return 'OK'
        else:  # type == 'R'
            if self.state == 'LOCKED-W':
                return 'NOK'
            else:
                self.state = 'LOCKED-R'
                deadline = time() + time_limit
                self.read_lock[client_id] = deadline
                return 'OK'

    def release(self):
        """
        Liberta o recurso incondicionalmente, alterando os valores associados
        ao bloqueio.
        """
        self.write_lock = (None, 0)
        self.read_lock = {}  # TODO necessário ?

    def unlock(self, type: str, client_id: str):
        """
        Liberta o recurso se este está bloqueado pelo cliente client_id.
        Retorna OK ou NOK.O desbloqueio pode ser relacionado a bloqueios 
        de escrita (type=W) ou de leitura (type=R), consoante o tipo.
        """
        if self.state == 'DISABLED' or self.state == 'UNLOCKED':
            return 'NOK'

        if type == 'W':
            if self.state == 'LOCKED-W' and self.write_lock[0] != client_id:
                return 'NOK'

            self.write_lock = (None, 0)
            self.state = 'UNLOCKED'

            return 'OK'
        else:  # type == 'R'
            if self.state == 'LOCKED-R' and client_id in self.read_lock:
                del self.read_lock[client_id]

                if len(self.read_lock) == 0:
                    self.state = 'UNLOCKED'

                return 'OK'

        # Se o cliente não tiver lock no recurso
        return 'NOK'

    # TODO perguntar ao prof já que não há encapsulamento
    def status(self):
        """
        Obtém o estado do recurso. Retorna LOCKED-W ou LOCKED-R ou UNLOCKED 
        ou DISABLED.
        """
        return self.state

    # TODO perguntar ao prof já que não há encapsulamento
    def stats(self):
        """
        Retorna o número de bloqueios de escrita feitos neste recurso. 
        """
        return self.write_lock_count

    def disable(self):
        """
        Coloca o recurso como desabilitado incondicionalmente, alterando os 
        valores associados à sua disponibilidade.
        """
        self.state = 'DISABLE'
        self.release()  # TODO necessário?

    def __repr__(self):
        """
        Representação da classe para a saída standard. A string devolvida por
        esta função é usada, por exemplo, se uma instância da classe for
        passada à função print ou str.
        """
        output = self.state
        # int maior =
        # Se o recurso está bloqueado para a escrita:
        # R <num do recurso> LOCKED-W <vezes bloqueios de escrita> <id do cliente> <deadline do bloqueio de escrita>
        if self.state == 'LOCKED-W':
            output = f' {self.write_lock_count} {self.self.write_lock[0]} {self.write_lock[1]}'
        # Se o recurso está bloqueado para a leitura:
        # R <num do recurso> LOCKED-R <vezes bloqueios de escrita> <num bloqueios de leitura atuais> <último deadline dos bloqueios de leitura>
        if self.state == 'LOCKED-R':
            output = f' {self.write_lock_count} {len(self.read_lock)} {max(self.read_lock.values())}'

        return output


###############################################################################

class lock_pool:
    def __init__(self, N: int, K: int):
        """
        Define um array com um conjunto de resource_locks para N recursos. 
        Os locks podem ser manipulados pelos métodos desta classe. 
        Define K, o número máximo de bloqueios de escrita permitidos para cada 
        recurso. Ao atingir K bloqueios de escrita, o recurso fica desabilitado.
        """
        self.resources = [resource_lock(i) for i in range(N)]
        self.max_resource_locks = K

    def clear_expired_locks(self):
        """
        Verifica se os recursos que estão bloqueados ainda estão dentro do tempo
        de concessão dos bloqueios. Remove os bloqueios para os quais o tempo de
        concessão tenha expirado.
        """
        for resource in self.resources:
            now = time()
            if resource.state == 'LOCKED-W':
                if resource.write_lock[1] != 0 and resource.write_lock[1] < now:
                    resource.release()
            elif resource.state == 'LOCKED-R':
                # TODO confirmar
                if all(t < now for t in resource.read_lock.values()):
                    resource.release()

    def lock(self, type: str, resource_id: int, client_id: str, time_limit: int):
        """
        Tenta bloquear (do tipo R ou W) o recurso resource_id pelo cliente client_id, 
        durante time_limit segundos. Retorna OK, NOK ou UNKNOWN RESOURCE.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return 'UNKNOWN RESOURCE'

        resource = self.resources[resource_id - 1]
        if type == 'W' and resource.write_lock_count >= self.max_resource_locks:
            return 'NOK'

        return resource.lock(type, client_id, time_limit)

    def unlock(self, type: str, resource_id: int, client_id: str):
        """
        Liberta o bloqueio (do tipo R ou W) sobre o recurso resource_id pelo cliente 
        client_id. Retorna OK, NOK ou UNKNOWN RESOURCE.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return 'UNKNOWN RESOURCE'

        resource = self.resources[resource_id - 1]
        return resource.unlock(type, client_id)

    def status(self, resource_id: int):
        """
        Obtém o estado de um recurso. Retorna LOCKED, UNLOCKED,
        DISABLED ou UNKNOWN RESOURCE.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return 'UNKNOWN RESOURCE'

        resource = self.resources[resource_id - 1]

        return resource.state

    def stats(self, option: str, resource_id: int):
        """
        Obtém o estado do serviço de gestão de bloqueios. Se option for K, retorna <número de 
        bloqueios feitos no recurso resource_id> ou UNKNOWN RESOURCE. Se option for N, retorna 
        <número de recursos bloqueados atualmente>. Se option for D, retorna 
        <número de recursos desabilitados>
        """
        if option == 'K':
            if resource_id < 1 or resource_id > len(self.resources):
                return 'UNKNOWN RESOURCE'

            resource = self.resources[resource_id - 1]

            return resource.write_lock_count
        elif option == 'N':
            return reduce(lambda acc, r: acc + int(r.state == 'UNLOCKED'), self.resources, 0)
        elif option == 'D':
            return reduce(lambda acc, r: acc + int(r.state == 'DISABLED'), self.resources, 0)
        else:
            return 'UNKNOWN OPTION'

    def __repr__(self):
        """
        Representação da classe para a saída standard. A string devolvida por
        esta função é usada, por exemplo, se uma instância da classe for
        passada à função print ou str.
        """
        return '\n'.join(
            map(lambda r, i: f'R {i + 1} {r}', enumerate(self.resources))
        )


###############################################################################

# código do programa principal
def parse() -> Dict[str, Union[str, int, bool, Tuple[str]]]:
    """
    Define o parser de argumentos.
    :return: Dict com valores dos argumentos escolhidos pelo utilizador.
    """
    parser = ArgumentParser(description='')

    parser.add_argument("address", help="IP ou Hostname onde o Servidor irá fornecer os recursos")

    parser.add_argument("port", help="Porto TCP onde escutará por pedidos de ligação", type=int)

    parser.add_argument("n", help="Número de recursos que serão geridos pelo Servidor")

    parser.add_argument("k", help="Número de bloqueios permitidos em cada recurso")

    args = parser.parse_args().__dict__

    return args


def main() -> None:
    try:
        args = parse()

        socket = sock_utils.create_tcp_server_socket(args['address'], args['port'], 1)
        while True:
            (conn_sock, (addr, port)) = socket.accept()

            print('ligado a %s no porto %s' % (addr, port))

            msg = conn_sock.recv(1024)
            print(f'recebi {msg.decode("utf-8")}')

            conn_sock.sendall(b'batatas')
            conn_sock.close()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
