"""Funcionalidades do perfil APURADOR."""
from database.db import conectar, votacao_aberta
from security.auth import exigir_perfil
from security.logger import registrar_log


def apurar(usuario):
    if not exigir_perfil(usuario, "apurador"):
        return
    if votacao_aberta():
        print("Resultados disponíveis apenas após o encerramento da votação.")
        return
    with conectar() as conn:
        linhas = conn.execute("""
            SELECT c.nome, COUNT(v.id) AS total
            FROM candidatos c LEFT JOIN votos v ON v.candidato_id = c.id
            GROUP BY c.id ORDER BY total DESC
        """).fetchall()
    registrar_log(usuario["username"], "APURACAO_CONSULTADA")
    print("\n--- Resultado ---")
    for l in linhas:
        print(f"{l['nome']}: {l['total']} voto(s)")
