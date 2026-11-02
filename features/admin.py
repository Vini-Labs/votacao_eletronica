"""Funcionalidades do perfil ADMIN."""
import sqlite3
from getpass import getpass

from database.db import conectar, votacao_aberta
from security.auth import criar_usuario, exigir_perfil
from security.logger import registrar_log


def cadastrar_usuario(usuario):
    if not exigir_perfil(usuario, "admin"):
        return
    username = input("Novo usuário: ").strip()
    senha = getpass("Senha: ")
    perfil = input("Perfil (admin/apurador/eleitor): ").strip().lower()
    _, msg = criar_usuario(username, senha, perfil, autor=usuario["username"])
    print(msg)


def cadastrar_candidato(usuario):
    if not exigir_perfil(usuario, "admin"):
        return
    nome = input("Nome do candidato: ").strip()
    if not (2 <= len(nome) <= 60):
        print("Nome inválido: use de 2 a 60 caracteres.")
        return
    try:
        with conectar() as conn:
            conn.execute("INSERT INTO candidatos (nome) VALUES (?)", (nome,))
    except sqlite3.IntegrityError:
        print("Esse candidato já está cadastrado.")
        return
    registrar_log(usuario["username"], "CANDIDATO_CRIADO", nome)
    print("Candidato cadastrado.")


def alternar_votacao(usuario):
    if not exigir_perfil(usuario, "admin"):
        return
    novo = "0" if votacao_aberta() else "1"
    with conectar() as conn:
        conn.execute("UPDATE config SET valor = ? WHERE chave = 'votacao_aberta'", (novo,))
    estado = "ABERTA" if novo == "1" else "ENCERRADA"
    registrar_log(usuario["username"], "VOTACAO_" + estado)
    print(f"Votação {estado.lower()}.")


def ver_logs(usuario):
    if not exigir_perfil(usuario, "admin"):
        return
    with conectar() as conn:
        linhas = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 20").fetchall()
    print("\n--- Últimos 20 registros ---")
    for l in linhas:
        print(f"{l['data_hora']} | {l['usuario']:<12} | {l['acao']:<24} | {l['detalhe']}")
