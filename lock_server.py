#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações Distribuídas - Projeto 1 - lock_server.py
Grupo: 21
Números de aluno: 56895, 56926
"""

# Zona para fazer importação
import traceback
from argparse import ArgumentParser
from time import time
from functools import reduce
from typing import Dict, Union, Tuple
import sock_utils


###############################################################################


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
                self.read_lock.append((client_id, deadline))
                return 'OK'

    def release(self):
        """
        Liberta o recurso incondicionalmente, alterando os valores associados
        ao bloqueio.
        """
        self.write_lock = (None, 0)
        self.read_lock = []
        self.state = 'UNLOCKED'

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
            if self.state == 'LOCKED-R':
                ok = False
                for i, concessao in enumerate(self.read_lock):
                    if concessao[0] == client_id:
                        self.read_lock.pop(i)

                if len(self.read_lock) == 0:
                    self.state = 'UNLOCKED'

                if ok:
                    return 'OK'

        # Se o cliente não tiver lock no recurso
        return 'NOK'

    def status(self):
        """
        Obtém o estado do recurso. Retorna LOCKED-W ou LOCKED-R ou UNLOCKED,
        ou DISABLED.
        """
        return self.state

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
        self.write_lock = (None, 0)
        self.read_lock = []
        self.state = 'DISABLE'

    def __repr__(self):
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

    def lock(self, type: str, resource_id: int, client_id: str, time_limit: int):
        """
        Tenta bloquear (do tipo R ou W) o recurso resource_id pelo cliente client_id, 
        durante time_limit segundos. Retorna OK, NOK ou UNKNOWN RESOURCE.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return 'UNKNOWN RESOURCE'

        resource = self.resources[resource_id - 1]
        if type == 'W' and resource.stats() >= self.max_resource_locks:
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

        res = resource.unlock(type, client_id)
        if resource.stats() >= self.max_resource_locks:
            resource.disable()

        return res

    def status(self, resource_id: int):
        """
        Obtém o estado de um recurso. Retorna LOCKED, UNLOCKED,
        DISABLED ou UNKNOWN RESOURCE.
        """
        if resource_id < 1 or resource_id > len(self.resources):
            return 'UNKNOWN RESOURCE'

        resource = self.resources[resource_id - 1]

        return resource.status()

    def stats(self, option: str, resource_id: int) -> Union[int, str]:
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

            return resource.stats()
        elif option == 'N':
            return reduce(lambda acc, r: acc + int(r.status() == 'UNLOCKED'), self.resources, 0)
        elif option == 'D':
            return reduce(lambda acc, r: acc + int(r.status() == 'DISABLED'), self.resources, 0)
        else:
            return 'UNKNOWN OPTION'

    def __repr__(self):
        """
        Representação da classe para a saída standard. A string devolvida por
        esta função é usada, por exemplo, se uma instância da classe for
        passada à função print ou str.
        """
        return '\n'.join(
            map(lambda r: f'R {r[0] + 1} {r[1]}', enumerate(self.resources))
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

    parser.add_argument("n", help="Número de recursos que serão geridos pelo Servidor", type=int)

    parser.add_argument("k", help="Número de bloqueios permitidos em cada recurso", type=int)

    args = parser.parse_args().__dict__

    return args


def main() -> None:
    try:
        args = parse()

        socket = sock_utils.create_tcp_server_socket(args['address'], args['port'], 1)
        pool = lock_pool(args['n'], args['k'])
        while True:
            (conn_sock, (addr, port)) = socket.accept()

            print(f'Ligado a {addr} no porto {port}')

            msg = conn_sock.recv(1024)
            cmd, *cargs = msg.decode('utf-8').split()

            res = []

            pool.clear_expired_locks()

            try:
                if len(cmd) == 0:
                    raise Exception('UNKNOWN COMMAND')

                if cmd == 'LOCK':
                    if len(cargs) < 4:
                        raise Exception('LOCK type, resource_id, time_limit, and client_id are required')
                    elif len(cargs) > 4:
                        raise Exception('LOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('LOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('LOCK resource_id must be a digit')

                    if not cargs[2].isdigit():
                        raise Exception('LOCK time_limit must be a digit')

                    resp = pool.lock(cargs[0], int(cargs[1]), cargs[3], int(cargs[2]))
                    res.append(resp)
                elif cmd == 'UNLOCK':
                    if len(cargs) < 3:
                        raise Exception('UNLOCK type, resource_id, and client_id are required')
                    elif len(cargs) > 3:
                        raise Exception('UNLOCK too many arguments')

                    if cargs[0] not in {'R', 'W'}:
                        raise Exception('UNLOCK type must be R or W')

                    if not cargs[1].isdigit():
                        raise Exception('UNLOCK resource_id must be a digit')

                    resp = pool.unlock(cargs[0], int(cargs[1]), cargs[2])
                    res.append(resp)
                elif cmd == 'STATUS':
                    if len(cargs) < 1:
                        raise Exception('STATUS resource_id is required')

                    resp = pool.status(int(cargs[0]))
                    res.append(resp)
                elif cmd == 'STATS':
                    if len(cargs) < 1:
                        raise Exception('STATS subcommand is required')
                    scmd, *sargs = cargs

                    if scmd == 'K':
                        if len(sargs) < 1:
                            raise Exception('STATS resource_id is required')
                        elif len(sargs) > 1:
                            raise Exception('STATS too many arguments')
                    elif scmd == 'N':
                        if len(cargs) > 1:
                            raise Exception('STATS too many arguments')
                    elif scmd == 'D':
                        if len(cargs) > 1:
                            raise Exception('STATS too many arguments')
                    else:
                        raise Exception('STATS subcommand must be K, N, or D')

                    resp = pool.stats(scmd, int(sargs[0]) if scmd == 'K' else None)
                    res.append(str(resp))
                elif cmd == 'PRINT':
                    res.append(str(pool))
            except Exception as e:
                print(e)
                continue

            parsed_res = ' '.join(res)
            conn_sock.sendall(parsed_res.encode('utf-8'))
            conn_sock.close()
    except KeyboardInterrupt:
        print('si señor')
        exit()
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    main()
