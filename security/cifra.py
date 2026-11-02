"""Sigilo do voto: o candidato escolhido é gravado cifrado (AES-256-GCM)."""
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from security.segredo import subchave

_ASSOCIADO = b"voto-v1"  # autentica o contexto: um texto cifrado de outro uso não vale como voto


def cifrar_voto(candidato_id):
    nonce = os.urandom(12)  # aleatório: o mesmo voto nunca gera o mesmo texto cifrado
    # Tamanho fixo (8 dígitos): o tamanho do texto cifrado não revela o número do candidato
    texto = f"{candidato_id:08d}".encode()
    return nonce + AESGCM(subchave("voto")).encrypt(nonce, texto, _ASSOCIADO)


def decifrar_voto(blob):
    """Devolve o id do candidato, ou None se o registro foi adulterado/é inválido."""
    try:
        texto = AESGCM(subchave("voto")).decrypt(blob[:12], blob[12:], _ASSOCIADO)
        return int(texto)
    except (InvalidTag, ValueError):
        return None
