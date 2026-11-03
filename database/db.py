"""Conexão com o SQLite e criação das tabelas."""
import sqlite3

from config import ABERTA, DB_PATH, NAO_INICIADA


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    with conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                senha_hash BLOB NOT NULL,
                perfil TEXT NOT NULL CHECK (perfil IN ('admin','apurador','eleitor')),
                ja_votou INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS candidatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL COLLATE NOCASE
            );
            -- Sem usuário, sem data e sem ordem: o voto é cifrado (AES-GCM, nonce aleatório)
            -- e a chave primária é o próprio texto cifrado (WITHOUT ROWID), então a ordem
            -- física no arquivo é aleatória e não dá para ligar um voto a quem votou.
            CREATE TABLE IF NOT EXISTS votos (
                voto_cifrado BLOB PRIMARY KEY
            ) WITHOUT ROWID;
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                acao TEXT NOT NULL,
                detalhe TEXT,
                data_hora TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tentativas_login (
                username TEXT PRIMARY KEY,
                falhas INTEGER NOT NULL DEFAULT 0,
                bloqueado_ate REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS config (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );
        """)
        conn.execute(
            "INSERT OR IGNORE INTO config (chave, valor) VALUES ('estado', ?)", (NAO_INICIADA,)
        )


def estado_votacao():
    with conectar() as conn:
        return conn.execute("SELECT valor FROM config WHERE chave = 'estado'").fetchone()["valor"]


def votacao_aberta():
    return estado_votacao() == ABERTA
