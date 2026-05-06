from database import get_connection


def autenticar_usuario(login, senha):
    """
    Verifica se login e senha estão corretos.
    Retorna os dados do usuário (como dicionário) ou None se inválido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE login = ? AND senha = ?",
        (login, senha)
    )
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        # Converte Row para dicionário para facilitar o uso nas views
        return dict(usuario)
    return None


def listar_usuarios():
    """Retorna todos os usuários cadastrados (sem a senha)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, login, perfil FROM usuarios")
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return usuarios


def criar_usuario(nome, login, senha, perfil):
    """
    Cria um novo usuário.
    Retorna True se criado com sucesso, False se o login já existe.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, login, senha, perfil) VALUES (?, ?, ?, ?)",
            (nome, login, senha, perfil)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERRO] Criar usuário: {e}")
        return False


def deletar_usuario(usuario_id):
    """Remove um usuário pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()