import tkinter as tk
from tkinter import ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from produto import listar_produtos

CORES = {
    "fundo": "#1E1E2E", "painel": "#2A2A3E",
    "primaria": "#7C3AED", "texto": "#F1F5F9",
    "texto_sub": "#94A3B8", "borda": "#3F3F5F",
    "verde": "#22C55E", "vermelho": "#EF4444",
}


class TelaVendedor(tk.Tk):
    """
    Painel do vendedor — somente visualização do estoque.
    Sem permissão para criar, editar ou deletar.
    """

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"PDV — Vendedor: {usuario['nome']}")
        self.geometry("860x540")
        self.configure(bg=CORES["fundo"])
        self._construir_ui()
        self._carregar_produtos()

    def _construir_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg=CORES["primaria"], padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="🏪 PDV Estoque",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="left")

        tk.Label(header, text=f"👤 {self.usuario['nome']}  |  Perfil: Vendedor",
                 font=("Segoe UI", 10),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="right")

        # ── Área principal ──
        main = tk.Frame(self, bg=CORES["fundo"], padx=20, pady=20)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="Consulta de Estoque",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(anchor="w")

        tk.Label(main, text="Você tem permissão apenas para visualizar os produtos.",
                 font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"]).pack(anchor="w", pady=(2, 12))

        # ── Tabela ──
        colunas = ("ID", "Nome", "Categoria", "Quantidade", "Preço", "Situação")
        self.tabela = ttk.Treeview(main, columns=colunas, show="headings", height=16)

        larguras = {"ID": 40, "Nome": 220, "Categoria": 130,
                    "Quantidade": 90, "Preço": 90, "Situação": 80}

        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras[col], anchor="center")

        # Estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=CORES["painel"],
                        foreground=CORES["texto"],
                        rowheight=28,
                        fieldbackground=CORES["painel"],
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background=CORES["borda"],
                        foreground=CORES["texto"],
                        font=("Segoe UI", 10, "bold"))

        self.tabela.pack(fill="both", expand=True)

        # Botão atualizar
        tk.Button(
            main, text="🔄  Atualizar",
            font=("Segoe UI", 10), bg=CORES["primaria"],
            fg=CORES["texto"], relief="flat", cursor="hand2",
            command=self._carregar_produtos
        ).pack(anchor="e", pady=(10, 0))

    def _carregar_produtos(self):
        """Busca e exibe os produtos no Treeview."""
        for row in self.tabela.get_children():
            self.tabela.delete(row)

        for p in listar_produtos():
            self.tabela.insert("", "end", values=(
                p["id"], p["nome"], p["categoria"],
                p["quantidade"], f"R$ {p['preco']:.2f}", p["situacao"].capitalize()
            ))