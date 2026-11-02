from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "votacao.db"

MAX_TENTATIVAS = 3
PERFIS = ("admin", "apurador", "eleitor")
