Como não estava dito o contrário, consideramos que um cliente pode bloquear o mesmo recurso para leitura várias vezes em simultâneo.
- Assim, quando faz unlock a um recurso que detém para leitura, irá remover todas as suas concessões.
- Isto também influencia o comando PRINT para retornar quantos clientes bloqueiam um recurso para escrita no momento

Optámos por fazer a verificação dos comandos do lado do cliente para minimizar os pedidos icorretos, e fazê-lo também do lado do servidor como garantia