/*
 Aplicações Distribuídas - Projeto 4 - server/schema.sql
 Grupo: 21
 Números de aluno: 56895, 56926
 Nomes de aluno: Matilde Silva, Lucas Pinto
 */
-- PRAGMA foreign_keys = ON;
CREATE TABLE utilizadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    senha TEXT
);

CREATE TABLE musicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_spotify TEXT UNIQUE,
    nome TEXT,
    id_artista INTEGER,
    FOREIGN KEY(id_artista) REFERENCES artistas(id) ON DELETE CASCADE
);

CREATE TABLE artistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_spotify TEXT UNIQUE,
    nome TEXT
);

CREATE TABLE avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sigla TEXT,
    designacao TEXT
);

CREATE TABLE playlists (
    id_user INTEGER,
    id_musica INTEGER,
    id_avaliacao INTEGER,
    PRIMARY KEY (id_user, id_musica),
    FOREIGN KEY(id_user) REFERENCES utilizadores(id) ON DELETE CASCADE,
    FOREIGN KEY(id_musica) REFERENCES musicas(id) ON DELETE CASCADE,
    FOREIGN KEY(id_avaliacao) REFERENCES avaliacoes(id) ON DELETE CASCADE
);

-- Default state
INSERT INTO
    avaliacoes (id, sigla, designacao)
VALUES
    (1, "M", "Medíocre"),
    (2, "m", "Mau"),
    (3, "S", "Suficiente"),
    (4, "B", "Boa"),
    (5, "MB", "Muito Boa");