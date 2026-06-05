from database import get_connection


def situacao_por_quantidade(quantidade):
    """Mantem a situacao coerente com a quantidade em estoque."""
    return "em_falta" if quantidade <= 0 else "reabastecido"


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
        situacao = situacao_por_quantidade(quantidade)
        cursor.execute(
            """
            INSERT INTO produtos (nome, categoria, quantidade, preco_compra, preco, situacao)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, categoria, quantidade, preco_compra, preco, situacao)
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
        situacao = situacao_por_quantidade(quantidade)
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
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    if not produto:
        conn.close()
        return False, "Produto nao encontrado."

    situacao_correta = situacao_por_quantidade(produto["quantidade"])
    if nova_situacao != situacao_correta:
        conn.close()
        return False, (
            "A situacao deve seguir a quantidade: estoque zerado fica em falta; "
            "estoque acima de zero fica reabastecido."
        )

    cursor.execute(
        "UPDATE produtos SET situacao = ? WHERE id = ?",
        (nova_situacao, produto_id)
    )
    conn.commit()
    conn.close()
    return True, "Situacao atualizada com sucesso."


def alterar_situacao_estoque(produto_id, nova_situacao, quantidade_reabastecida=None):
    """Altera a situacao mantendo quantidade e status coerentes."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            conn.close()
            return False, "Produto nao encontrado."

        if nova_situacao == "em_falta":
            nova_quantidade = 0
        elif nova_situacao == "reabastecido":
            if produto["quantidade"] > 0:
                nova_quantidade = produto["quantidade"]
            else:
                if quantidade_reabastecida is None or quantidade_reabastecida <= 0:
                    conn.close()
                    return False, "Informe uma quantidade maior que zero para reabastecer."
                nova_quantidade = quantidade_reabastecida
        else:
            conn.close()
            return False, "Situacao invalida."

        cursor.execute("""
            UPDATE produtos
            SET quantidade = ?, situacao = ?
            WHERE id = ?
        """, (nova_quantidade, nova_situacao, produto_id))
        conn.commit()
        conn.close()
        return True, "Situacao atualizada com sucesso."
    except Exception as e:
        print(f"[ERRO] Alterar situacao: {e}")
        return False, "Nao foi possivel atualizar a situacao."


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
        nova_situacao = situacao_por_quantidade(nova_quantidade)

        cursor.execute("""
            INSERT INTO vendas (
                produto_id, produto_nome, categoria, quantidade,
                preco_compra, preco_venda, status, usuario_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            produto_id, produto["nome"], produto["categoria"], quantidade,
            produto["preco_compra"], produto["preco"], "registrada", usuario_id
        ))
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
        filtro = "WHERE COALESCE(NULLIF(v.categoria, ''), p.categoria) = ?"
        params.append(categoria)

    cursor.execute(f"""
        SELECT
            COALESCE(v.produto_id, 0) AS id,
            COALESCE(NULLIF(v.produto_nome, ''), p.nome, 'Produto removido') AS nome,
            COALESCE(NULLIF(v.categoria, ''), p.categoria, 'Sem categoria') AS categoria,
            COALESCE(SUM(v.quantidade), 0) AS quantidade_vendida,
            COALESCE(SUM(v.quantidade * v.preco_compra), 0) AS total_compra,
            COALESCE(SUM(v.quantidade * v.preco_venda), 0) AS total_venda,
            COALESCE(SUM(v.quantidade * (v.preco_venda - v.preco_compra)), 0) AS lucro
        FROM vendas v
        LEFT JOIN produtos p ON p.id = v.produto_id
        {filtro}
        GROUP BY
            COALESCE(NULLIF(v.produto_nome, ''), p.nome, 'Produto removido'),
            COALESCE(NULLIF(v.categoria, ''), p.categoria, 'Sem categoria')
        ORDER BY
            COALESCE(NULLIF(v.produto_nome, ''), p.nome, 'Produto removido')
    """, params)
    itens = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return itens


def listar_saidas(categoria=None):
    """Retorna todas as saidas/vendas registradas."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    filtro = ""
    if categoria:
        filtro = "WHERE COALESCE(NULLIF(v.categoria, ''), p.categoria) = ?"
        params.append(categoria)

    cursor.execute(f"""
        SELECT
            v.id,
            v.data_venda,
            COALESCE(NULLIF(v.produto_nome, ''), p.nome, 'Produto removido') AS produto,
            COALESCE(NULLIF(v.categoria, ''), p.categoria, 'Sem categoria') AS categoria,
            v.quantidade,
            v.preco_compra,
            v.preco_venda,
            v.status,
            (v.quantidade * v.preco_compra) AS total_compra,
            (v.quantidade * v.preco_venda) AS total_venda,
            (v.quantidade * (v.preco_venda - v.preco_compra)) AS lucro,
            COALESCE(u.nome, 'Nao informado') AS vendedor
        FROM vendas v
        LEFT JOIN produtos p ON p.id = v.produto_id
        LEFT JOIN usuarios u ON u.id = v.usuario_id
        {filtro}
        ORDER BY v.data_venda DESC, v.id DESC
    """, params)
    saidas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return saidas
