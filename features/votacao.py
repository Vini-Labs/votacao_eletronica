"""Funcionalidades do perfil ELEITOR."""
from config import ABERTA
from database.db import conectar, votacao_aberta
from security.auth import exigir_perfil
from security.cifra import cifrar_voto
from security.logger import registrar_log
from security.validacoes import ler_inteiro


def votar(usuario):
    if not exigir_perfil(usuario, "eleitor"):
        return
    if not votacao_aberta():
        print("A votação não está aberta.")
        return

    with conectar() as conn:
        candidatos = conn.execute("SELECT id, nome FROM candidatos ORDER BY id").fetchall()
        ja_votou = conn.execute(
            "SELECT ja_votou FROM usuarios WHERE id = ?", (usuario["id"],)
        ).fetchone()["ja_votou"]

    if ja_votou:
        registrar_log(usuario["username"], "VOTO_DUPLICADO_BLOQUEADO")
        print("Voto já registrado para este eleitor.")
        return
    if not candidatos:
        print("Não há candidatos cadastrados.")
        return

    print("\n--- Candidatos ---")
    for c in candidatos:
        print(f"{c['id']}. {c['nome']}")

    escolha = ler_inteiro("Número do candidato: ")
    if escolha not in [c["id"] for c in candidatos]:
        print("Candidato inválido.")
        return
    if input("Confirmar voto? (s/n): ").strip().lower() != "s":
        print("Voto cancelado.")
        return

    with conectar() as conn:
        # UPDATE condicional garante voto único mesmo em tentativas simultâneas
        cur = conn.execute(
            "UPDATE usuarios SET ja_votou = 1 WHERE id = ? AND ja_votou = 0", (usuario["id"],)
        )
        if cur.rowcount == 0:
            print("Voto já registrado para este eleitor.")
            return
        # Reconfere dentro da mesma transação (a votação pode ter sido encerrada agora)
        estado = conn.execute("SELECT valor FROM config WHERE chave = 'estado'").fetchone()["valor"]
        if estado != ABERTA:
            conn.rollback()
            print("A votação foi encerrada. Voto não registrado.")
            return
        # O voto vai cifrado, sem usuário, sem data e sem ordem
        conn.execute("INSERT INTO votos (voto_cifrado) VALUES (?)", (cifrar_voto(escolha),))
    registrar_log(usuario["username"], "VOTO_REGISTRADO")  # registra quem votou, não em quem
    print("Voto registrado com sucesso.")
