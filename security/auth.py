"""Autenticação (login) e autorização (checagem de perfil)."""
import sqlite3
from getpass import getpass

from config import MAX_TENTATIVAS, PERFIS
from database.db import conectar
from security.logger import registrar_log
from security.privacidade import rotulo
from security.senhas import checar_senha, gerar_hash
from security.validacoes import validar_senha, validar_username


def criar_usuario(username, senha, perfil, autor="sistema"):
    if not validar_username(username):
        return False, "Usuário inválido: use 3 a 20 letras, números ou _."
    if not validar_senha(senha):
        return False, "Senha fraca: mínimo de 8 caracteres, com letras e números."
    if perfil not in PERFIS:
        return False, "Perfil inválido."
    try:
        with conectar() as conn:
            conn.execute(
                "INSERT INTO usuarios (username, senha_hash, perfil) VALUES (?, ?, ?)",
                (username, gerar_hash(senha), perfil),
            )
    except sqlite3.IntegrityError:
        return False, "Esse nome de usuário já existe."
    registrar_log(autor, "USUARIO_CRIADO", f"{rotulo(username, perfil)} ({perfil})")
    return True, "Usuário criado com sucesso."


def login():
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        username = input("Usuário: ").strip()
        senha = getpass("Senha: ")
        with conectar() as conn:
            u = conn.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
        if u and checar_senha(senha, u["senha_hash"]):
            registrar_log(username, "LOGIN_OK")
            return dict(u)
        registrar_log(username or "(vazio)", "LOGIN_FALHA", f"tentativa {tentativa}/{MAX_TENTATIVAS}")
        # Mensagem genérica: não revela se o usuário existe ou se a senha está errada
        print("Usuário ou senha inválidos.")
    print("Número máximo de tentativas excedido.")
    return None


def exigir_perfil(usuario, *perfis):
    """Checagem de autorização feita dentro de cada função restrita."""
    if usuario["perfil"] not in perfis:
        registrar_log(usuario["username"], "ACESSO_NEGADO", f"perfil {usuario['perfil']}")
        print("Acesso negado: seu perfil não tem permissão para esta ação.")
        return False
    return True
