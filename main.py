"""Sistema de Votação Eletrônica - ponto de entrada."""
from getpass import getpass

from database.db import conectar, criar_tabelas
from features.menus import menu_usuario
from security.auth import criar_usuario, login


def primeiro_acesso():
    """Sem senha padrão no código: o admin é criado na primeira execução."""
    with conectar() as conn:
        total = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    if total > 0:
        return
    print("Primeiro acesso: crie a conta do administrador.")
    while True:
        username = input("Usuário admin: ").strip()
        senha = getpass("Senha: ")
        ok, msg = criar_usuario(username, senha, "admin")
        print(msg)
        if ok:
            return


def main():
    criar_tabelas()
    primeiro_acesso()
    while True:
        print("\n=== Sistema de Votação Eletrônica ===")
        print("1. Login")
        print("0. Sair")
        op = input("> ").strip()
        if op == "1":
            usuario = login()
            if usuario:
                menu_usuario(usuario)
        elif op == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
