"""Privacidade nos logs: eleitores e apuradores aparecem como pseudônimos.

O pseudônimo é estável (mesma pessoa -> mesmo código, útil para auditar), mas não dá
para descobrir o nome a partir dele sem o segredo local. Administradores aparecem
com o nome, pois quem administra deve ser responsabilizável.
"""
import hashlib
import hmac

from database.db import conectar
from security.segredo import subchave


def pseudonimo(username, perfil):
    h = hmac.new(subchave("log"), username.lower().encode(), hashlib.sha256).hexdigest()[:6]
    return f"{perfil}#{h}"


def rotulo(username, perfil):
    return username if perfil == "admin" else pseudonimo(username, perfil)


def rotulo_de_usuario_existente(username):
    """Rótulo seguro para logs. Nomes digitados que não existem NÃO são gravados
    (podem ser senhas digitadas no campo errado ou texto malicioso)."""
    if username == "sistema":
        return username
    with conectar() as conn:
        u = conn.execute("SELECT username, perfil FROM usuarios WHERE username = ?", (username,)).fetchone()
    if u is None:
        return "(desconhecido)"
    return rotulo(u["username"], u["perfil"])
