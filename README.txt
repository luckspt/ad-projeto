Aplicações Distribuídas - Projeto 4 - README.txt
Grupo: 21
Números de aluno: 56895, 56926
Nomes de aluno: Matilde Silva, Lucas Pinto

# Instruções de execução:
## Servidor
```bash
cd grupo21/server
python3 main.py localhost 9999
```

Usar `python3 main.py -h` para ver a ajuda/descrições dos argumentos

## Cliente
```bash
cd grupo21/client
python3 main.py localhost 9999
```

Usar `python3 main.py -h` para ver a ajuda/descrições dos argumentos

# Requisitos
sqlite3 >= 3.35.0 (https://www.sqlite.org/releaselog/3_35_0.html, ponto 4) devido à adição do comando `RETURNING`. Usar o ficheiro `main_presqlite.py` para versões anteriores.
dotenv (`pip3 install python-dotenv`) para carregar o ID e SECRET da app do Spotify - `cd grupo21/server`, `cp .env.example .env`, `nano .env`
json >= 3.5 o package requests levanta uma exceção que apenas existe a partir desta versão (https://docs.python.org/3.5/library/json.html#json.JSONDecodeError)

# Notas
- Usámos o package dotenv para as variáveis de ambiente (Client ID e Secret).
    - Basta copiar o ficheiro **.env.example** para um **.env** (`cp .env.example .env`) e incluir as chaves `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET`
- Classe `Spotify` que abstrai os métodos necessários (GET Artist e GET Track) para o funcionamento do serviço, que agora utiliza o módulo OAuth2Session
- Classe `Playlists` que abstrai os métodos necessários para a comunicação do cliente com o serviço, cliente da classe `Reqs` referida anteriormente

# Modificações ao Projeto 3
- verificação do sqlite < 3.35.0 que corria num import do ficheiro `main_presqlite.py` movida para a função main
- agora apenas existe uma conexão global à BD, definida na thread principal que inicializa o Flask, e usada pelos threads dos endpoints da API (ignoramos o problema de concorrência)
