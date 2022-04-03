Aplicações Distribuídas - Projeto 2 - README.txt
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto

Como não estava dito o contrário, consideramos que um cliente pode bloquear o mesmo recurso para leitura várias vezes em simultâneo
- Assim, quando faz UNLOCK a um recurso (ou a concessão expira), irá remover uma concessões de cada vez  desse recurso;
- Isto também influencia o comando PRINT para retornar quantos clientes bloqueiam um recurso para escrita no momento.
