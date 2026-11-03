# Sistema de Votação Eletrônica

Projeto de Desenvolvimento de Software Seguro (terminal, Python + SQLite).

## Como rodar
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Na primeira execução são criados `votacao.db` (dados) e `segredo.key` (chave local).
**Os dois ficam fora do Git** (ver `.gitignore`). Cada pessoa que clonar o projeto começa com banco vazio e cria o próprio admin.
Se `segredo.key` for apagado, os votos já gravados não podem mais ser lidos.

## Regras da eleição
- Estados: `não iniciada → aberta → encerrada` (não volta atrás).
- Candidatos e eleitores só podem ser cadastrados **antes** da abertura; mínimo de 2 candidatos e 1 eleitor para abrir.
- Resultados só após o encerramento.

## Segurança
- Senhas com hash bcrypt; login com bloqueio de 5 min após 3 falhas (vale também para usuários inexistentes), com contagem regressiva do tempo restante.
- Usuário: começa com letra e tem ao menos 3 letras (nada de só números).
- Logs: consulta com filtros (usuário, ação, período) e paginação.
- Voto cifrado com AES-256-GCM, gravado sem usuário, data ou ordem; decifrado só na apuração.
- Logs: eleitores e apuradores aparecem como pseudônimo (ex.: `eleitor#9c4405`); admins aparecem com o nome.

## Estrutura
- `config.py` — constantes (caminhos, limites, estados)
- `database/` — conexão e criação das tabelas SQLite
- `security/` — hash de senha, validação, autenticação, cifra do voto, pseudônimos e logs
- `features/` — funcionalidades por perfil (admin, eleitor, apurador) e menus
- `main.py` — ponto de entrada
