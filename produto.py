from database import get_connection


def listar_produtos():
    """Retorna todos os produtos do estoque."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos


def buscar_produto(produto_id):
    """Retorna um produto específico pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    conn.close()
    return dict(produto) if produto else None


def criar_produto(nome, categoria, quantidade, preco):
    """Cadastra um novo produto no estoque."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, categoria, quantidade, preco) VALUES (?, ?, ?, ?)",
            (nome, categoria, quantidade, preco)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERRO] Criar produto: {e}")
        return False


def atualizar_produto(produto_id, nome, categoria, quantidade, preco, situacao):
    """Atualiza os dados de um produto existente."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produtos
            SET nome = ?, categoria = ?, quantidade = ?, preco = ?, situacao = ?
            WHERE id = ?
        """, (nome, categoria, quantidade, preco, situacao, produto_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERRO] Atualizar produto: {e}")
        return False


def deletar_produto(produto_id):
    """Remove um produto pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()


def atualizar_situacao(produto_id, nova_situacao):
    """Reabastecida ou Em falta um produto rapidamente."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET situacao = ? WHERE id = ?",
        (nova_situacao, produto_id)
    )
    conn.commit()
    conn.close()