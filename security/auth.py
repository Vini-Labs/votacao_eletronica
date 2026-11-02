"""Autenticação (login com bloqueio de tentativas) e autorização (checagem de perfil)."""
import hashlib
import hmac
import sqlite3
import time
from getpass import getpass

from config import BLOQUEIO_SEGUNDOS, MAX_TENTATIVAS, PERFIS
from database.db import conectar
from security.logger import registrar_log
from security.privacidade import rotulo
from security.segredo import subchave
from security.senhas import checar_senha, gerar_hash
from security.validacoes import validar_senha, validar_username

_hash_falso = None


def _hash_para_usuario_inexistente():
    """Hash de enganação: gasta o mesmo tempo de bcrypt mesmo se o usuário não existe."""
    global _hash_falso
    if _hash_falso is None:
        _hash_falso = gerar_hash("senha-falsa-para-igualar-tempo")
    return _hash_falso


def _chave_tentativas(username):
    # Guardamos só um HMAC do que foi digitado (nunca o texto), valendo também para
    # usuários que não existem: assim o bloqueio não revela quem está cadastrado.
    return hmac.new(subchave("login"), username.strip().lower().encode(), hashlib.sha256).hexdigest()


def _segundos_bloqueado(chave):
    with conectar() as conn:
        linha = conn.execute(
            "SELECT bloqueado_ate FROM tentativas_login WHERE username = ?", (chave,)
        ).fetchone()
    if linha is None:
        return 0
    restante = linha["bloqueado_ate"] - time.time()
    return int(restante) + 1 if restante > 0 else 0


def _contagem_regressiva(chave):
    """Mostra o tempo restante do bloqueio, atualizando a cada segundo (Ctrl+C volta ao menu)."""
    print("Login bloqueado. (Ctrl+C para voltar ao menu)")
    try:
        while True:
            restante = _segundos_bloqueado(chave)
            if restante <= 0:
                break
            print(f"\rTempo restante: {restante // 60:02d}:{restante % 60:02d}  ", end="", flush=True)
            time.sleep(1)
        print("\rBloqueio encerrado. Você já pode tentar novamente.      ")
    except KeyboardInterrupt:
        print()


def _registrar_falha(chave):
    """Soma uma falha; ao atingir o limite, bloqueia. Devolve o total de falhas."""
    with conectar() as conn:
        conn.execute(
            "INSERT INTO tentativas_login (username, falhas) VALUES (?, 1) "
            "ON CONFLICT(username) DO UPDATE SET falhas = falhas + 1",
            (chave,),
        )
        falhas = conn.execute(
            "SELECT falhas FROM tentativas_login WHERE username = ?", (chave,)
        ).fetchone()["falhas"]
        if falhas >= MAX_TENTATIVAS:
            conn.execute(
                "UPDATE tentativas_login SET bloqueado_ate = ? WHERE username = ?",
                (time.time() + BLOQUEIO_SEGUNDOS, chave),
            )
    return falhas


def _limpar_falhas(chave):
    with conectar() as conn:
        conn.execute("DELETE FROM tentativas_login WHERE username = ?", (chave,))


def criar_usuario(username, senha, perfil, autor="sistema"):
    if not validar_username(username):
        return False, "Usuário inválido: 3 a 20 caracteres (letras, números ou _), começando por letra e com ao menos 3 letras."
    if not validar_senha(senha):
        return False, "Senha fraca: mínimo de 8 caracteres, com letras e números."
    if perfil not in PERFIS:
        return False, "Perfil inválido."
    try:
        with conectar() as conn:
            conn.execute(
                "INSERT INTO usuarios (username, senha_hash, perfil) VALUES (?, ?, ?)",
                (username, gerar_hash(senha), perfil),
            )
    except sqlite3.IntegrityError:
        return False, "Esse nome de usuário já existe."
    registrar_log(autor, "USUARIO_CRIADO", f"{rotulo(username, perfil)} ({perfil})")
    return True, "Usuário criado com sucesso."


def login():
    for _ in range(MAX_TENTATIVAS):
        username = input("Usuário: ").strip()
        senha = getpass("Senha: ")
        chave = _chave_tentativas(username)

        restante = _segundos_bloqueado(chave)
        if restante:
            registrar_log(username, "LOGIN_BLOQUEADO")
            print("Muitas tentativas para este usuário.")
            _contagem_regressiva(chave)
            return None

        with conectar() as conn:
            u = conn.execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
        hash_conferido = u["senha_hash"] if u else _hash_para_usuario_inexistente()
        senha_ok = checar_senha(senha, hash_conferido)

        if u and senha_ok:
            _limpar_falhas(chave)
            registrar_log(u["username"], "LOGIN_OK")
            return dict(u)

        falhas = _registrar_falha(chave)
        registrar_log(username, "LOGIN_FALHA", f"falha {falhas}")
        # Mensagem genérica: não revela se o usuário existe ou se a senha está errada
        print("Usuário ou senha inválidos.")
        time.sleep(1)  # freia tentativas automáticas
        if falhas >= MAX_TENTATIVAS:
            break
    print("Número máximo de tentativas excedido.")
    _contagem_regressiva(chave)
    return None


def exigir_perfil(usuario, *perfis):
    """Checagem de autorização feita dentro de cada função restrita."""
    if usuario["perfil"] not in perfis:
        registrar_log(usuario["username"], "ACESSO_NEGADO", f"perfil {usuario['perfil']}")
        print("Acesso negado: seu perfil não tem permissão para esta ação.")
        return False
    return True
