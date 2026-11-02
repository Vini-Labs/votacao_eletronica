"""Menus de cada perfil."""
from features.admin import alternar_votacao, cadastrar_candidato, cadastrar_usuario, ver_logs
from features.resultados import apurar
from features.votacao import votar
from security.logger import registrar_log
from security.validacoes import ler_inteiro

MENUS = {
    "admin": [
        ("Cadastrar usuário", cadastrar_usuario),
        ("Cadastrar candidato", cadastrar_candidato),
        ("Abrir/encerrar votação", alternar_votacao),
        ("Ver logs", ver_logs),
    ],
    "apurador": [("Ver resultados", apurar)],
    "eleitor": [("Votar", votar)],
}


def menu_usuario(usuario):
    opcoes = MENUS[usuario["perfil"]]
    while True:
        print(f"\n=== {usuario['username']} ({usuario['perfil']}) ===")
        for i, (titulo, _) in enumerate(opcoes, start=1):
            print(f"{i}. {titulo}")
        print("0. Sair da conta")
        op = ler_inteiro("> ")
        if op == 0:
            registrar_log(usuario["username"], "LOGOUT")
            return
        if op is None or not (1 <= op <= len(opcoes)):
            print("Opção inválida.")
            continue
        opcoes[op - 1][1](usuario)
