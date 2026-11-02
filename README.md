# Sistema de Votação Eletrônica

Projeto de Desenvolvimento de Software Seguro (terminal, Python + SQLite).

## Como rodar
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Estrutura
- `config.py` — constantes (caminho do banco, limite de tentativas)
- `database/` — conexão e criação das tabelas SQLite
- `security/` — hash de senha, validação, autenticação/autorização e logs
- `features/` — funcionalidades por perfil (admin, eleitor, apurador) e menus
- `main.py` — ponto de entrada
