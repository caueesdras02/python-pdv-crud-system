import sqlite3
import os

# Caminho do banco de dados (fica na mesma pasta do projeto)
DB_PATH = os.path.join(os.path.dirname(__file__), "estoque.db")


def get_connection():
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn


def inicializar_banco():
    """
    Cria as tabelas do banco de dados, caso ainda não existam.
    Chamada uma única vez ao iniciar o sistema.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários (vendedor ou gerente)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nome     TEXT    NOT NULL,
            login    TEXT    NOT NULL UNIQUE,
            senha    TEXT    NOT NULL,
            perfil   TEXT    NOT NULL CHECK(perfil IN ('vendedor', 'gerente'))
        )
    """)

    # Tabela de produtos (estoque)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            categoria   TEXT    NOT NULL,
            quantidade  INTEGER NOT NULL DEFAULT 0,
            preco       REAL    NOT NULL DEFAULT 0.0,
            situacao    TEXT    NOT NULL DEFAULT 'reabastecido' CHECK(situacao IN ('reabastecido', 'em_falta'))
        )
    """)

    # Insere usuários padrão para teste, se ainda não existirem
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios_padrao = [
            ("Gerente Padrão", "gerente", "1234", "gerente"),
            ("Vendedor Padrão", "vendedor", "1234", "vendedor"),
        ]
        cursor.executemany(
            "INSERT INTO usuarios (nome, login, senha, perfil) VALUES (?, ?, ?, ?)",
            usuarios_padrao
        )
        print("[DB] Usuários padrão criados: gerente/1234 e vendedor/1234")

    conn.commit()
    conn.close()
    print("[DB] Banco de dados inicializado com sucesso.")