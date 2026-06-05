import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from produto import (
    listar_produtos, listar_categorias, buscar_produto, registrar_saida,
    alterar_situacao_estoque
)

CORES = {
    "fundo": "#1E1E2E", "painel": "#2A2A3E",
    "primaria": "#7C3AED", "texto": "#F1F5F9",
    "texto_sub": "#94A3B8", "borda": "#3F3F5F",
    "verde": "#22C55E", "vermelho": "#EF4444",
}


class TelaVendedor(tk.Tk):
    """Painel do vendedor - consulta estoque e registra saidas/vendas."""

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"PDV - Vendedor: {usuario['nome']}")
        self.geometry("940x580")
        self.configure(bg=CORES["fundo"])
        self._construir_menu()
        self._construir_ui()
        self._carregar_produtos()

    def _construir_menu(self):
        menu = tk.Menu(self)
        sistema = tk.Menu(menu, tearoff=0)
        sistema.add_command(label="Trocar usuario", command=self._trocar_usuario)
        sistema.add_separator()
        sistema.add_command(label="Sair", command=self.destroy)
        menu.add_cascade(label="Sistema", menu=sistema)
        self.config(menu=menu)

    def _trocar_usuario(self):
        self.destroy()
        from login import TelaLogin
        TelaLogin().mainloop()

    def _construir_ui(self):
        header = tk.Frame(self, bg=CORES["primaria"], padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="PDV Estoque",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="left")

        tk.Label(header, text=f"Usuario: {self.usuario['nome']}  |  Perfil: Vendedor",
                 font=("Segoe UI", 10),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="right")

        main = tk.Frame(self, bg=CORES["fundo"], padx=20, pady=20)
        main.pack(fill="both", expand=True)

        barra = tk.Frame(main, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 12))

        tk.Label(barra, text="Consulta de Estoque",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(side="left")

        tk.Button(
            barra, text="Registrar Saida",
            font=("Segoe UI", 10, "bold"), bg=CORES["verde"],
            fg=CORES["texto"], relief="flat", cursor="hand2",
            padx=12, pady=6, command=self._abrir_registro_saida
        ).pack(side="right", padx=4)

        tk.Button(
            barra, text="Atualizar Situacao",
            font=("Segoe UI", 10, "bold"), bg=CORES["primaria"],
            fg=CORES["texto"], relief="flat", cursor="hand2",
            padx=12, pady=6, command=self._alternar_situacao
        ).pack(side="right", padx=4)

        filtro = tk.Frame(main, bg=CORES["fundo"])
        filtro.pack(fill="x", pady=(0, 12))
        tk.Label(filtro, text="Categoria:",
                 font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"]).pack(side="left")
        self.categoria_var = tk.StringVar(value="Todas")
        self.combo_categoria = ttk.Combobox(
            filtro, textvariable=self.categoria_var,
            state="readonly", width=24
        )
        self.combo_categoria.pack(side="left", padx=8)
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self._carregar_produtos())

        colunas = ("ID", "Nome", "Categoria", "Quantidade", "Venda", "Situacao")
        self.tabela = ttk.Treeview(main, columns=colunas, show="headings", height=16)

        larguras = {
            "ID": 40, "Nome": 240, "Categoria": 140,
            "Quantidade": 100, "Venda": 100, "Situacao": 90
        }

        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras[col], anchor="center")

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

    def _atualizar_categorias(self):
        categoria_atual = self.categoria_var.get()
        categorias = ["Todas"] + listar_categorias()
        self.combo_categoria["values"] = categorias
        if categoria_atual in categorias:
            self.categoria_var.set(categoria_atual)
        else:
            self.categoria_var.set("Todas")

    def _categoria_filtrada(self):
        categoria = self.categoria_var.get()
        return None if categoria == "Todas" else categoria

    def _carregar_produtos(self):
        self._atualizar_categorias()
        for row in self.tabela.get_children():
            self.tabela.delete(row)

        for p in listar_produtos(self._categoria_filtrada()):
            self.tabela.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nome"], p["categoria"], p["quantidade"],
                f"R$ {p['preco']:.2f}", p["situacao"].capitalize()
            ))

    def _produto_selecionado(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Atencao", "Selecione um produto na tabela.")
            return None
        return int(selecionado[0])

    def _abrir_registro_saida(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        FormSaida(self, produto, self._salvar_saida)

    def _alternar_situacao(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        nova = "em_falta" if produto["situacao"] == "reabastecido" else "reabastecido"
        quantidade = None
        if nova == "reabastecido" and produto["quantidade"] <= 0:
            quantidade = simpledialog.askinteger(
                "Reabastecer",
                "Informe a quantidade reabastecida:",
                parent=self,
                minvalue=1
            )
            if quantidade is None:
                return

        if nova == "em_falta" and produto["quantidade"] > 0:
            confirmar = messagebox.askyesno(
                "Confirmar",
                "Marcar como em falta vai zerar a quantidade em estoque. Deseja continuar?"
            )
            if not confirmar:
                return

        ok, mensagem = alterar_situacao_estoque(pid, nova, quantidade)
        self._carregar_produtos()
        if ok:
            messagebox.showinfo("Sucesso", mensagem)
        else:
            messagebox.showerror("Erro", mensagem)

    def _salvar_saida(self, produto_id, quantidade):
        ok, mensagem = registrar_saida(produto_id, quantidade, self.usuario.get("id"))
        if ok:
            messagebox.showinfo("Sucesso", mensagem)
            self._carregar_produtos()
        else:
            messagebox.showerror("Erro", mensagem)


class FormSaida(tk.Toplevel):
    """Janela para registrar saida/venda de um produto."""

    def __init__(self, parent, produto, callback):
        super().__init__(parent)
        self.title("Registrar Saida")
        self.geometry("380x260")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.grab_set()
        self.produto = produto
        self.callback = callback
        self._construir_form()

    def _construir_form(self):
        tk.Label(self, text=self.produto["nome"], font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(anchor="w", padx=24, pady=(20, 4))
        info = (
            f"Estoque atual: {self.produto['quantidade']}   |   "
            f"Preco: R$ {self.produto['preco']:.2f}"
        )
        tk.Label(self, text=info, font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"]).pack(anchor="w", padx=24, pady=(0, 18))

        tk.Label(self, text="Quantidade vendida *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", padx=24)
        self.e_quantidade = tk.Entry(self, font=("Segoe UI", 12),
                                     bg=CORES["painel"], fg=CORES["texto"],
                                     insertbackground=CORES["texto"], relief="flat")
        self.e_quantidade.pack(fill="x", padx=24, ipady=6, pady=(6, 8))
        self.e_quantidade.focus()

        self.lbl_erro = tk.Label(self, text="", font=("Segoe UI", 9),
                                 bg=CORES["fundo"], fg=CORES["vermelho"])
        self.lbl_erro.pack()

        tk.Button(
            self, text="Registrar", font=("Segoe UI", 11, "bold"),
            bg=CORES["verde"], fg=CORES["texto"], relief="flat",
            cursor="hand2", command=self._salvar
        ).pack(fill="x", padx=24, ipady=8, pady=8)

    def _salvar(self):
        quantidade = self.e_quantidade.get().strip()
        if not quantidade:
            self.lbl_erro.config(text="Informe a quantidade vendida.")
            return

        try:
            quantidade = int(quantidade)
        except ValueError:
            self.lbl_erro.config(text="Quantidade deve ser um numero inteiro.")
            return

        if quantidade <= 0:
            self.lbl_erro.config(text="Quantidade deve ser maior que zero.")
            return

        self.destroy()
        self.callback(self.produto["id"], quantidade)
