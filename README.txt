Aplicações Distribuídas - Projeto 3 - README.txt
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto

# Instruções de execução:
## Servidor
```bash
cd src/server
python3 main.py localhost 9999
```

Usar `python3 main.py -h` para ver a ajuda/descrições dos argumentos

## Cliente
```bash
cd src/client
python3 main.py localhost 9999
```

Usar `python3 main.py -h` para ver a ajuda/descrições dos argumentos

# Requisitos
Versão do sqlite3 >= 3.35.0 (https://www.sqlite.org/releaselog/3_35_0.html, ponto 4) devido à adição do comando `RETURNING`. Usar o ficheiro `main_presqlite.py` para versões anteriores.
dotenv (`pip3 install python-dotenv`)

# Notas
- Adicionámos AUTOINCREMENT no schema visto que os ids são sequenciais
- Alterámos a row_factory do sqlite para `sqlite3.Row` de forma a obtermos dicionários em vez de tuplos nos pedidos à base de dados
- Implementámos um `errorhandler` e um tipo de exceção (`ApiException`) para tratar da descrição detalhada de problemas
    - Os *links* `describedBy` e `supportId` são fictícios
- Usámos o package dotenv para as variáveis de ambiente (OAuth2 token do Spotify).
    - Basta copiar o ficheiro **.env.example** para um **.env** (`cp .env.example .env`) e incluir um token
- Classe `Reqs` que abstrai os pedidos GET/POST/PUT/DELETE
- Classe `Spotify` que abstrai os métodos necessários (GET Artist e GET Track) para o funcionamento do serviço, cliente da classe `Reqs` referida anteriormente
- Classe `Playlists` que abstrai os métodos necessários para a comunicação do cliente com o serviço, cliente da classe `Reqs` referida anteriormente
