"""Segredo local do sistema. Gerado uma vez, guardado fora do Git (ver .gitignore).

Dele derivamos duas subchaves independentes: uma para cifrar votos e outra
para gerar os pseudônimos usados nos logs.
"""
import hashlib
import hmac
import os

from config import SEGREDO_PATH


def _segredo_mestre():
    if not SEGREDO_PATH.exists():
        fd = os.open(SEGREDO_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(os.urandom(32))
    dados = SEGREDO_PATH.read_bytes()
    if len(dados) != 32:
        raise RuntimeError("segredo.key corrompido. Sem ele os votos já gravados não podem ser lidos.")
    return dados


def subchave(finalidade):
    return hmac.new(_segredo_mestre(), finalidade.encode(), hashlib.sha256).digest()
