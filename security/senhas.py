"""Proteção de credenciais: senhas só existem no banco como hash bcrypt."""
import bcrypt


def gerar_hash(senha):
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())


def checar_senha(senha, senha_hash):
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash)
