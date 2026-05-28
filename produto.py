from database import get_connection


def listar_produtos(categoria=None):
    """Retorna todos os produtos do estoque."""
    conn = get_connection()
    cursor = conn.cursor()
    if categoria:
        cursor.execute(
            "SELECT * FROM produtos WHERE categoria = ? ORDER BY nome",
            (categoria,)
        )
    else:
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos


def listar_categorias():
    """Retorna as categorias cadastradas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM produtos ORDER BY categoria")
    categorias = [row["categoria"] for row in cursor.fetchall()]
    conn.close()
    return categorias


def buscar_produto(produto_id):
    """Retorna um produto específico pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    conn.close()
    return dict(produto) if produto else None


def criar_produto(nome, categoria, quantidade, preco_compra, preco):
    """Cadastra um novo produto no estoque."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, categoria, quantidade, preco_compra, preco) VALUES (?, ?, ?, ?, ?)",
            (nome, categoria, quantidade, preco_compra, preco)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERRO] Criar produto: {e}")
        return False


def atualizar_produto(produto_id, nome, categoria, quantidade, preco_compra, preco, situacao):
    """Atualiza os dados de um produto existente."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produtos
            SET nome = ?, categoria = ?, quantidade = ?, preco_compra = ?, preco = ?, situacao = ?
            WHERE id = ?
        """, (nome, categoria, quantidade, preco_compra, preco, situacao, produto_id))
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


def registrar_saida(produto_id, quantidade, usuario_id=None):
    """Registra uma venda/saida e baixa a quantidade do estoque."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()

        if not produto:
            conn.close()
            return False, "Produto nao encontrado."

        if quantidade <= 0:
            conn.close()
            return False, "A quantidade deve ser maior que zero."

        if produto["quantidade"] < quantidade:
            conn.close()
            return False, "Quantidade insuficiente em estoque."

        nova_quantidade = produto["quantidade"] - quantidade
        nova_situacao = "em_falta" if nova_quantidade == 0 else produto["situacao"]

        cursor.execute("""
            INSERT INTO vendas (produto_id, quantidade, preco_compra, preco_venda, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        """, (produto_id, quantidade, produto["preco_compra"], produto["preco"], usuario_id))
        cursor.execute("""
            UPDATE produtos
            SET quantidade = ?, situacao = ?
            WHERE id = ?
        """, (nova_quantidade, nova_situacao, produto_id))

        conn.commit()
        conn.close()
        return True, "Saida registrada com sucesso."
    except Exception as e:
        print(f"[ERRO] Registrar saida: {e}")
        return False, "Nao foi possivel registrar a saida."


def relatorio_lucros(categoria=None):
    """Calcula lucro com base nas vendas registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    filtro = ""
    if categoria:
        filtro = "WHERE p.categoria = ?"
        params.append(categoria)

    cursor.execute(f"""
        SELECT
            p.id,
            p.nome,
            p.categoria,
            COALESCE(SUM(v.quantidade), 0) AS quantidade_vendida,
            COALESCE(SUM(v.quantidade * v.preco_compra), 0) AS total_compra,
            COALESCE(SUM(v.quantidade * v.preco_venda), 0) AS total_venda,
            COALESCE(SUM(v.quantidade * (v.preco_venda - v.preco_compra)), 0) AS lucro
        FROM produtos p
        LEFT JOIN vendas v ON v.produto_id = p.id
        {filtro}
        GROUP BY p.id, p.nome, p.categoria
        ORDER BY p.nome
    """, params)
    itens = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return itens
