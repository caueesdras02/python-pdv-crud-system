"""
PDV Estoque — Sistema de Controle de Estoque
Trabalho Acadêmico — Desenvolvimento Rápido em Python

Como executar:
    python main.py

Credenciais de teste:
    Gerente  → login: gerente  | senha: 1234
    Vendedor → login: vendedor | senha: 1234
"""

import sys
import os

# Garante que os imports funcionem independente de onde o script é chamado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import inicializar_banco
from login import TelaLogin


if __name__ == "__main__":
    # 1. Inicializa o banco de dados (cria as tabelas se não existirem)
    inicializar_banco()

    # 2. Abre a tela de login
    app = TelaLogin()
    app.mainloop()