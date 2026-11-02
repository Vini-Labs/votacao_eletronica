"""Registro de ações relevantes (quem, o quê, quando)."""
from datetime import datetime

from database.db import conectar


def registrar_log(usuario, acao, detalhe=""):
    with conectar() as conn:
        conn.execute(
            "INSERT INTO logs (usuario, acao, detalhe, data_hora) VALUES (?, ?, ?, ?)",
            (usuario, acao, detalhe, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
