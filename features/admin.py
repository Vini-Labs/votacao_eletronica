"""Funcionalidades do perfil ADMIN."""
import re
import sqlite3
from datetime import datetime
from getpass import getpass

from config import ABERTA, ENCERRADA, MIN_CANDIDATOS, NAO_INICIADA
from database.db import conectar, estado_votacao
from security.auth import criar_usuario, exigir_perfil
from security.logger import registrar_log


def cadastrar_usuario(usuario):
    if not exigir_perfil(usuario, "admin"):
        return
    username = input("Novo usuário: ").strip()
    senha = getpass("Senha: ")
    perfil = input("Perfil (admin/apurador/eleitor): ").strip().lower()
    # Eleitor novo com a votação já aberta/encerrada permitiria criar "votos fantasma"
    if perfil == "eleitor" and estado_votacao() != NAO_INICIADA:
        registrar_log(usuario["username"], "CADASTRO_ELEITOR_BLOQUEADO", estado_votacao())
        print("Eleitores só podem ser cadastrados antes da abertura da votação.")
        return
    _, msg = criar_usuario(username, senha, perfil, autor=usuario["username"])
    print(msg)


def cadastrar_candidato(usuario):
    if not exigir_perfil(usuario, "admin"):
        return
    # Candidato só entra antes da votação começar: não muda a disputa com ela em andamento
    if estado_votacao() != NAO_INICIADA:
        registrar_log(usuario["username"], "CANDIDATO_BLOQUEADO", estado_votacao())
        print("Candidatos só podem ser cadastrados antes da abertura da votação.")
        return
    nome = " ".join(input("Nome do candidato: ").split())  # tira espaços repetidos
    # Só letras (com acento) e espaços entre os nomes; sem números nem símbolos
    if not (2 <= len(nome) <= 60) or not re.fullmatch(r"[^\W\d_]+(?: [^\W\d_]+)*", nome):
        print("Nome inválido: use apenas letras e espaços (2 a 60 caracteres).")
        return
    try:
        with conectar() as conn:
            conn.execute("INSERT INTO candidatos (nome) VALUES (?)", (nome,))
    except sqlite3.IntegrityError:
        print("Esse candidato já está cadastrado.")
        return
    registrar_log(usuario["username"], "CANDIDATO_CRIADO", nome)
    print("Candidato cadastrado.")


def _transicao(de, para):
    """Troca o estado só se ele ainda for `de` (evita corrida)."""
    with conectar() as conn:
        cur = conn.execute(
            "UPDATE config SET valor = ? WHERE chave = 'estado' AND valor = ?", (para, de)
        )
    return cur.rowcount == 1


def alternar_votacao(usuario):
    """Abre a votação (1x) e a encerra (definitivo). Não é possível reabrir."""
    if not exigir_perfil(usuario, "admin"):
        return
    estado = estado_votacao()

    if estado == ENCERRADA:
        print("A votação já foi encerrada e não pode ser reaberta.")
        return

    if estado == NAO_INICIADA:
        with conectar() as conn:
            n_cand = conn.execute("SELECT COUNT(*) FROM candidatos").fetchone()[0]
            n_eleit = conn.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'eleitor'").fetchone()[0]
        if n_cand < MIN_CANDIDATOS:
            print(f"Cadastre ao menos {MIN_CANDIDATOS} candidatos antes de abrir a votação.")
            return
        if n_eleit < 1:
            print("Cadastre ao menos 1 eleitor antes de abrir a votação.")
            return
        print("Ao abrir, não será mais possível cadastrar candidatos nem eleitores.")
        if input("Abrir a votação? (s/n): ").strip().lower() != "s":
            print("Operação cancelada.")
            return
        if _transicao(NAO_INICIADA, ABERTA):
            registrar_log(usuario["username"], "VOTACAO_ABERTA")
            print("Votação aberta.")
        return

    # estado == ABERTA
    print("Encerrar é DEFINITIVO: a votação não poderá ser reaberta.")
    if input("Encerrar a votação? (s/n): ").strip().lower() != "s":
        print("Operação cancelada.")
        return
    if _transicao(ABERTA, ENCERRADA):
        registrar_log(usuario["username"], "VOTACAO_ENCERRADA")
        print("Votação encerrada.")


POR_PAGINA = 10


def _ler_data(msg):
    """Lê data AAAA-MM-DD (ou vazio). Devolve (ok, valor)."""
    txt = input(msg).strip()
    if not txt:
        return True, None
    try:
        return True, datetime.strptime(txt, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        print("Data inválida. Use AAAA-MM-DD (ex.: 2026-11-02).")
        return False, None


def ver_logs(usuario):
    """Consulta de logs com filtros (usuário, ação, período) e paginação."""
    if not exigir_perfil(usuario, "admin"):
        return
    print("\n--- Consulta de logs (deixe em branco para não filtrar) ---")
    print("Obs.: eleitores e apuradores aparecem como pseudônimo (ex.: eleitor#9c4405).")
    quem = input("Usuário/pseudônimo (parte do nome): ").strip()
    acao = input("Ação (parte do nome, ex.: LOGIN): ").strip()
    ok, de = _ler_data("Data inicial (AAAA-MM-DD): ")
    if not ok:
        return
    ok, ate = _ler_data("Data final   (AAAA-MM-DD): ")
    if not ok:
        return
    if de and ate and de > ate:
        print("A data inicial não pode ser maior que a final.")
        return

    where, params = [], []
    esc = lambda t: t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    if quem:
        where.append("usuario LIKE ? ESCAPE '\\'")
        params.append(f"%{esc(quem)}%")
    if acao:
        where.append("acao LIKE ? ESCAPE '\\'")
        params.append(f"%{esc(acao.upper())}%")
    if de:
        where.append("data_hora >= ?")
        params.append(f"{de} 00:00:00")
    if ate:
        where.append("data_hora <= ?")
        params.append(f"{ate} 23:59:59")
    filtro = (" WHERE " + " AND ".join(where)) if where else ""

    with conectar() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM logs{filtro}", params).fetchone()[0]
    if total == 0:
        print("Nenhum registro encontrado.")
        return

    paginas = -(-total // POR_PAGINA)
    pagina = 1
    while True:
        with conectar() as conn:
            linhas = conn.execute(
                f"SELECT * FROM logs{filtro} ORDER BY id DESC LIMIT ? OFFSET ?",
                params + [POR_PAGINA, (pagina - 1) * POR_PAGINA],
            ).fetchall()
        print(f"\n--- Página {pagina}/{paginas} ({total} registros) ---")
        for l in linhas:
            print(f"{l['data_hora']} | {l['usuario']:<16} | {l['acao']:<26} | {l['detalhe']}")
        cmd = input("[p] próxima  [a] anterior  [n] nº da página  [s] sair: ").strip().lower()
        if cmd == "p" and pagina < paginas:
            pagina += 1
        elif cmd == "a" and pagina > 1:
            pagina -= 1
        elif cmd == "n":
            try:
                alvo = int(input(f"Página (1-{paginas}): ").strip())
            except ValueError:
                alvo = 0
            if 1 <= alvo <= paginas:
                pagina = alvo
            else:
                print("Página inválida.")
        elif cmd == "s":
            break
