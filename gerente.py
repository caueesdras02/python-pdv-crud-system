import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from produto import (listar_produtos, criar_produto,
                             atualizar_produto, deletar_produto,
                             atualizar_situacao, buscar_produto)

CORES = {
    "fundo": "#1E1E2E", "painel": "#2A2A3E",
    "primaria": "#7C3AED", "primaria_h": "#6D28D9",
    "texto": "#F1F5F9", "texto_sub": "#94A3B8",
    "borda": "#3F3F5F", "verde": "#22C55E",
    "vermelho": "#EF4444", "amarelo": "#F59E0B",
}


class TelaGerente(tk.Tk):
    """
    Painel do gerente — CRUD completo de produtos.
    """

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"PDV — Gerente: {usuario['nome']}")
        self.geometry("960x600")
        self.configure(bg=CORES["fundo"])
        self._construir_ui()
        self._carregar_produtos()

    # ── Interface ────────────────────────────
    def _construir_ui(self):
        # Header
        header = tk.Frame(self, bg=CORES["primaria"], padx=20, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="🏪 PDV Estoque — Gerente",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="left")
        tk.Label(header, text=f"👤 {self.usuario['nome']}",
                 font=("Segoe UI", 10),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="right")

        # Área principal
        main = tk.Frame(self, bg=CORES["fundo"], padx=20, pady=16)
        main.pack(fill="both", expand=True)

        # Barra de ações
        barra = tk.Frame(main, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 12))

        tk.Label(barra, text="Controle de Estoque",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(side="left")

        for (texto, cor, cmd) in [
            ("➕  Novo Produto",    CORES["verde"],    self._abrir_form_criar),
            ("✏️  Editar",          CORES["amarelo"],  self._editar_produto),
            ("🔄  Situação",        CORES["primaria"], self._alternar_situacao),
            ("🗑️  Deletar",         CORES["vermelho"], self._deletar_produto),
        ]:
            tk.Button(
                barra, text=texto, font=("Segoe UI", 10, "bold"),
                bg=cor, fg=CORES["texto"], relief="flat", cursor="hand2",
                padx=12, pady=6, command=cmd
            ).pack(side="right", padx=4)

        # Tabela
        colunas = ("ID", "Nome", "Categoria", "Quantidade", "Preço", "Situação")
        self.tabela = ttk.Treeview(main, columns=colunas, show="headings", height=18)

        larguras = {"ID": 40, "Nome": 240, "Categoria": 140,
                    "Quantidade": 100, "Preço": 100, "Situação": 90}

        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras[col], anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=CORES["painel"], foreground=CORES["texto"],
                        rowheight=28, fieldbackground=CORES["painel"],
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background=CORES["borda"], foreground=CORES["texto"],
                        font=("Segoe UI", 10, "bold"))

        self.tabela.pack(fill="both", expand=True)
        self.tabela.tag_configure("em_falta", foreground="#64748B")

    def _carregar_produtos(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)

        for p in listar_produtos():
            tag = "em_falta" if p["situacao"] == "em_falta" else ""
            self.tabela.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nome"], p["categoria"],
                p["quantidade"], f"R$ {p['preco']:.2f}", p["situacao"].capitalize()
            ), tags=(tag,))

    def _produto_selecionado(self):
        """Retorna o ID do produto selecionado na tabela, ou None."""
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto na tabela.")
            return None
        return int(selecionado[0])

    # ── Ações CRUD ───────────────────────────
    def _abrir_form_criar(self):
        FormProduto(self, titulo="Novo Produto", callback=self._salvar_novo)

    def _salvar_novo(self, dados):
        ok = criar_produto(dados["nome"], dados["categoria"],
                           dados["quantidade"], dados["preco"])
        if ok:
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            self._carregar_produtos()
        else:
            messagebox.showerror("Erro", "Não foi possível cadastrar o produto.")

    def _editar_produto(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        FormProduto(self, titulo="Editar Produto", produto=produto,
                    callback=lambda d: self._salvar_edicao(pid, d))

    def _salvar_edicao(self, pid, dados):
        ok = atualizar_produto(pid, dados["nome"], dados["categoria"],
                               dados["quantidade"], dados["preco"], dados["situacao"])
        if ok:
            messagebox.showinfo("Sucesso", "Produto atualizado!")
            self._carregar_produtos()

    def _alternar_situacao(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        nova = "em_falta" if produto["situacao"] == "reabastecido" else "reabastecido"
        atualizar_situacao(pid, nova)
        self._carregar_produtos()

    def _deletar_produto(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        confirmar = messagebox.askyesno(
            "Confirmar", f"Deseja deletar o produto '{produto['nome']}'?\nEssa ação não pode ser desfeita."
        )
        if confirmar:
            deletar_produto(pid)
            self._carregar_produtos()


# ── Formulário de Produto (criar / editar) ────
class FormProduto(tk.Toplevel):
    """Janela modal para criar ou editar um produto."""

    def __init__(self, parent, titulo, callback, produto=None):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x420")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.grab_set()  # Bloqueia a janela principal enquanto o form está aberto
        self.callback = callback
        self.produto = produto
        self._construir_form()

    def _construir_form(self):
        pad = {"padx": 24, "pady": 6}
        p = self.produto or {}

        tk.Label(self, text="Nome do Produto *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
        self.e_nome = self._entry(p.get("nome", ""))

        tk.Label(self, text="Categoria *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
        self.e_cat = self._entry(p.get("categoria", ""))

        tk.Label(self, text="Quantidade *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
        self.e_qtd = self._entry(str(p.get("quantidade", "0")))

        tk.Label(self, text="Preço (R$) *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
        self.e_preco = self._entry(str(p.get("preco", "0.00")))

        # Situação — só aparece na edição
        if self.produto:
            tk.Label(self, text="Situação", font=("Segoe UI", 10),
                     bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
            self.situacao_var = tk.StringVar(value=p.get("situacao", "reabastecido"))
            frame_sit = tk.Frame(self, bg=CORES["fundo"])
            frame_sit.pack(anchor="w", padx=24)
            for val in ("reabastecido", "em_falta"):
                tk.Radiobutton(frame_sit, text=val.capitalize(), value=val,
                               variable=self.situacao_var,
                               bg=CORES["fundo"], fg=CORES["texto"],
                               selectcolor=CORES["primaria"],
                               activebackground=CORES["fundo"]).pack(side="left", padx=8)

        self.lbl_erro = tk.Label(self, text="", font=("Segoe UI", 9),
                                 bg=CORES["fundo"], fg=CORES["vermelho"])
        self.lbl_erro.pack()

        tk.Button(
            self, text="Salvar", font=("Segoe UI", 11, "bold"),
            bg=CORES["primaria"], fg=CORES["texto"], relief="flat",
            cursor="hand2", command=self._salvar
        ).pack(fill="x", padx=24, ipady=8, pady=8)

    def _entry(self, valor=""):
        e = tk.Entry(self, font=("Segoe UI", 12),
                     bg=CORES["painel"], fg=CORES["texto"],
                     insertbackground=CORES["texto"], relief="flat")
        e.insert(0, valor)
        e.pack(fill="x", padx=24, ipady=6)
        return e

    def _salvar(self):
        nome  = self.e_nome.get().strip()
        cat   = self.e_cat.get().strip()
        qtd   = self.e_qtd.get().strip()
        preco = self.e_preco.get().strip()

        if not all([nome, cat, qtd, preco]):
            self.lbl_erro.config(text="⚠ Preencha todos os campos obrigatórios.")
            return

        try:
            qtd   = int(qtd)
            preco = float(preco)
        except ValueError:
            self.lbl_erro.config(text="⚠ Quantidade deve ser inteiro e Preço deve ser número.")
            return

        dados = {"nome": nome, "categoria": cat, "quantidade": qtd, "preco": preco}
        if self.produto:
            dados["situacao"] = self.situacao_var.get()

        self.destroy()
        self.callback(dados)