from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "votacao.db"
# Segredo local (gerado na 1a execução, fora do Git): cifra dos votos e pseudônimos dos logs
SEGREDO_PATH = BASE_DIR / "segredo.key"

MAX_TENTATIVAS = 3
PERFIS = ("admin", "apurador", "eleitor")
