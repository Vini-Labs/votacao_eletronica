from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "votacao.db"
# Segredo local (gerado na 1a execução, fora do Git): cifra dos votos e pseudônimos dos logs
SEGREDO_PATH = BASE_DIR / "segredo.key"

MAX_TENTATIVAS = 3
BLOQUEIO_SEGUNDOS = 300  # bloqueio após MAX_TENTATIVAS falhas seguidas
PERFIS = ("admin", "apurador", "eleitor")

# Estados da eleição (só avançam, nunca voltam): nao_iniciada -> aberta -> encerrada
NAO_INICIADA = "nao_iniciada"
ABERTA = "aberta"
ENCERRADA = "encerrada"
MIN_CANDIDATOS = 2
