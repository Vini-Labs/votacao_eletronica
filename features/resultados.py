"""Funcionalidades do perfil APURADOR."""
from config import ENCERRADA
from database.db import conectar, estado_votacao
from security.auth import exigir_perfil
from security.cifra import decifrar_voto
from security.logger import registrar_log


def apurar(usuario):
    if not exigir_perfil(usuario, "apurador"):
        return
    if estado_votacao() != ENCERRADA:
        print("Resultados disponíveis apenas após o encerramento da votação.")
        return
    with conectar() as conn:
        candidatos = conn.execute("SELECT id, nome FROM candidatos").fetchall()
        cifrados = [r["voto_cifrado"] for r in conn.execute("SELECT voto_cifrado FROM votos")]

    # A decifragem só acontece aqui, na apuração
    contagem = {c["id"]: 0 for c in candidatos}
    invalidos = 0
    for blob in cifrados:
        cid = decifrar_voto(blob)
        if cid in contagem:
            contagem[cid] += 1
        else:
            invalidos += 1  # adulterado ou de candidato inexistente

    registrar_log(usuario["username"], "APURACAO_CONSULTADA")
    print("\n--- Resultado ---")
    for c in sorted(candidatos, key=lambda c: -contagem[c["id"]]):
        print(f"{c['nome']}: {contagem[c['id']]} voto(s)")
    print(f"Total de votos: {len(cifrados)}")
    if invalidos:
        print(f"ATENÇÃO: {invalidos} voto(s) inválido(s) (possível adulteração).")
