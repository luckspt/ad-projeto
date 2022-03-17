Aplicações Distribuídas - Projeto 2 - README.txt
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto

Como não estava dito o contrário, consideramos que um cliente pode bloquear o mesmo recurso para leitura várias vezes em simultâneo
- Assim, quando faz UNLOCK a um recurso (ou a concessão expira), irá remover todas as concessões que detém desse recurso;
- Isto também influencia o comando PRINT para retornar quantos clientes bloqueiam um recurso para escrita no momento.

Optámos por fazer a verificação dos comandos do lado do cliente para minimizar os pedidos icorretos, e fazê-lo também do lado do servidor como garantia.

Uma vez que o comando STATS N está descrito que a resposta do servidor é o "número de recursos
UNLOCKED", escolhemos implementar desta forma, ao contrário do que a docstring do método resource_pool.stats() diz "se option for N, retorna <número de recursos bloqueados atualmente>".

Implementámos também a sintaxe dos comandos LOCK e UNLOCK com espaço, como descrito na Tabela 1, ao invés de com hífen, como está nos exemplos da Tabela 3.

Quanto aos recursos, decidimos começar o seu identificador por 1 dadas as condições de "recurso inexistente" referidas na especificação dos comandos LOCK e UNLOCK ("um número de recurso menor que 1 ou maior que N"), ao invés de começar por 0 como é visível nos exemplos
