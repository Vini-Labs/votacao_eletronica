"""Validação das entradas do usuário."""
import re


def validar_username(username):
    """3 a 20 caracteres (letras, números, _), começando com letra e com ao menos 3 letras.
    Assim 'user_1' e 'pedro' passam, mas '12345' ou '_____' não."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,19}", username):
        return False
    return sum(c.isalpha() for c in username) >= 3


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
