"""Registro de ações relevantes (quem, o quê, quando) sem expor eleitores/apuradores."""
from datetime import datetime

from database.db import conectar
from security.privacidade import rotulo_de_usuario_existente


def registrar_log(usuario, acao, detalhe=""):
    # O nome real de eleitor/apurador nunca chega ao banco de logs: só o pseudônimo.
    quem = rotulo_de_usuario_existente(usuario)
    with conectar() as conn:
        conn.execute(
            "INSERT INTO logs (usuario, acao, detalhe, data_hora) VALUES (?, ?, ?, ?)",
            (quem, acao, detalhe, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
