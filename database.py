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
            preco_compra REAL    NOT NULL DEFAULT 0.0,
            preco       REAL    NOT NULL DEFAULT 0.0,
            situacao    TEXT    NOT NULL DEFAULT 'reabastecido' CHECK(situacao IN ('reabastecido', 'em_falta'))
        )
    """)

    cursor.execute("PRAGMA table_info(produtos)")
    colunas_produtos = [coluna[1] for coluna in cursor.fetchall()]
    if "preco_compra" not in colunas_produtos:
        cursor.execute("ALTER TABLE produtos ADD COLUMN preco_compra REAL NOT NULL DEFAULT 0.0")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id     INTEGER NOT NULL,
            produto_nome   TEXT    NOT NULL DEFAULT '',
            categoria      TEXT    NOT NULL DEFAULT '',
            quantidade     INTEGER NOT NULL,
            preco_compra   REAL    NOT NULL,
            preco_venda    REAL    NOT NULL,
            status         TEXT    NOT NULL DEFAULT 'registrada',
            data_venda     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            usuario_id     INTEGER,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("PRAGMA table_info(vendas)")
    colunas_vendas = [coluna[1] for coluna in cursor.fetchall()]
    for nome_coluna, definicao in [
        ("produto_nome", "TEXT NOT NULL DEFAULT ''"),
        ("categoria", "TEXT NOT NULL DEFAULT ''"),
        ("status", "TEXT NOT NULL DEFAULT 'registrada'"),
    ]:
        if nome_coluna not in colunas_vendas:
            cursor.execute(f"ALTER TABLE vendas ADD COLUMN {nome_coluna} {definicao}")

    cursor.execute("""
        UPDATE vendas
        SET
            produto_nome = COALESCE((SELECT nome FROM produtos WHERE produtos.id = vendas.produto_id), produto_nome),
            categoria = COALESCE((SELECT categoria FROM produtos WHERE produtos.id = vendas.produto_id), categoria)
        WHERE produto_nome = '' OR categoria = ''
    """)

    cursor.execute("""
        UPDATE produtos
        SET situacao = CASE
            WHEN quantidade <= 0 THEN 'em_falta'
            ELSE 'reabastecido'
        END
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
