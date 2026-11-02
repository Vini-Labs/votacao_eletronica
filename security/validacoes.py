"""Validação das entradas do usuário."""
import re


def validar_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", username))


def validar_senha(senha):
    return (
        len(senha) >= 8
        and any(c.isalpha() for c in senha)
        and any(c.isdigit() for c in senha)
    )


def ler_inteiro(mensagem):
    """Lê um número do teclado; devolve None se a entrada for inválida."""
    try:
        return int(input(mensagem).strip())
    except ValueError:
        return None
