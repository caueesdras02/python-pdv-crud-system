import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from produto import (
    listar_produtos, criar_produto, atualizar_produto, deletar_produto,
    atualizar_situacao, buscar_produto, listar_categorias, relatorio_lucros,
    listar_saidas, alterar_situacao_estoque
)

CORES = {
    "fundo": "#1E1E2E", "painel": "#2A2A3E",
    "primaria": "#7C3AED", "primaria_h": "#6D28D9",
    "texto": "#F1F5F9", "texto_sub": "#94A3B8",
    "borda": "#3F3F5F", "verde": "#22C55E",
    "vermelho": "#EF4444", "amarelo": "#F59E0B",
}


class TelaGerente(tk.Tk):
    """Painel do gerente - CRUD completo de produtos e relatorio de lucros."""

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"PDV - Gerente: {usuario['nome']}")
        self.geometry("1080x620")
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

        relatorios = tk.Menu(menu, tearoff=0)
        relatorios.add_command(label="Lucros", command=self._abrir_relatorio_lucros)
        relatorios.add_command(label="Saidas registradas", command=self._abrir_relatorio_saidas)
        menu.add_cascade(label="Relatorios", menu=relatorios)
        self.config(menu=menu)

    def _trocar_usuario(self):
        self.destroy()
        from login import TelaLogin
        TelaLogin().mainloop()

    def _construir_ui(self):
        header = tk.Frame(self, bg=CORES["primaria"], padx=20, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="PDV Estoque - Gerente",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="left")
        tk.Label(header, text=f"Usuario: {self.usuario['nome']}",
                 font=("Segoe UI", 10),
                 bg=CORES["primaria"], fg=CORES["texto"]).pack(side="right")

        main = tk.Frame(self, bg=CORES["fundo"], padx=20, pady=16)
        main.pack(fill="both", expand=True)

        barra = tk.Frame(main, bg=CORES["fundo"])
        barra.pack(fill="x", pady=(0, 12))

        tk.Label(barra, text="Controle de Estoque",
                 font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(side="left")

        for texto, cor, cmd in [
            ("Novo Produto", CORES["verde"], self._abrir_form_criar),
            ("Editar", CORES["amarelo"], self._editar_produto),
            ("Relatorio de Lucros", CORES["verde"], self._abrir_relatorio_lucros),
            ("Relatorio de Saidas", CORES["primaria"], self._abrir_relatorio_saidas),
            ("Atualizar Situacao", CORES["primaria"], self._alternar_situacao),
            ("Deletar", CORES["vermelho"], self._deletar_produto),
        ]:
            tk.Button(
                barra, text=texto, font=("Segoe UI", 10, "bold"),
                bg=cor, fg=CORES["texto"], relief="flat", cursor="hand2",
                padx=12, pady=6, command=cmd
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

        colunas = ("ID", "Nome", "Categoria", "Quantidade", "Compra", "Venda", "Situacao")
        self.tabela = ttk.Treeview(main, columns=colunas, show="headings", height=18)

        larguras = {
            "ID": 40, "Nome": 240, "Categoria": 140, "Quantidade": 100,
            "Compra": 100, "Venda": 100, "Situacao": 90
        }

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
            tag = "em_falta" if p["situacao"] == "em_falta" else ""
            self.tabela.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nome"], p["categoria"], p["quantidade"],
                f"R$ {p['preco_compra']:.2f}", f"R$ {p['preco']:.2f}",
                p["situacao"].capitalize()
            ), tags=(tag,))

    def _produto_selecionado(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Atencao", "Selecione um produto na tabela.")
            return None
        return int(selecionado[0])

    def _abrir_form_criar(self):
        FormProduto(self, titulo="Novo Produto", callback=self._salvar_novo)

    def _salvar_novo(self, dados):
        ok = criar_produto(
            dados["nome"], dados["categoria"], dados["quantidade"],
            dados["preco_compra"], dados["preco"]
        )
        if ok:
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            self._carregar_produtos()
        else:
            messagebox.showerror("Erro", "Nao foi possivel cadastrar o produto.")

    def _editar_produto(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        FormProduto(self, titulo="Editar Produto", produto=produto,
                    callback=lambda d: self._salvar_edicao(pid, d))

    def _salvar_edicao(self, pid, dados):
        ok = atualizar_produto(
            pid, dados["nome"], dados["categoria"], dados["quantidade"],
            dados["preco_compra"], dados["preco"], dados["situacao"]
        )
        if ok:
            messagebox.showinfo("Sucesso", "Produto atualizado!")
            self._carregar_produtos()

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

    def _deletar_produto(self):
        pid = self._produto_selecionado()
        if pid is None:
            return
        produto = buscar_produto(pid)
        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Deseja deletar o produto '{produto['nome']}'?\nEssa acao nao pode ser desfeita."
        )
        if confirmar:
            deletar_produto(pid)
            self._carregar_produtos()

    def _abrir_relatorio_lucros(self):
        RelatorioLucros(self, self._categoria_filtrada())

    def _abrir_relatorio_saidas(self):
        RelatorioSaidas(self, self._categoria_filtrada())


class FormProduto(tk.Toplevel):
    """Janela modal para criar ou editar um produto."""

    def __init__(self, parent, titulo, callback, produto=None):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("430x500")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.grab_set()
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
        self.e_qtd = self._entry("" if not self.produto else str(p.get("quantidade", "")))

        tk.Label(self, text="Preco de compra (R$) *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
        self.e_preco_compra = self._entry("" if not self.produto else str(p.get("preco_compra", "")))

        tk.Label(self, text="Preco de venda (R$) *", font=("Segoe UI", 10),
                 bg=CORES["fundo"], fg=CORES["texto_sub"], anchor="w").pack(fill="x", **pad)
        self.e_preco = self._entry("" if not self.produto else str(p.get("preco", "")))

        if self.produto:
            tk.Label(self, text="Situacao", font=("Segoe UI", 10),
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
        nome = self.e_nome.get().strip()
        cat = self.e_cat.get().strip()
        qtd = self.e_qtd.get().strip()
        preco_compra = self.e_preco_compra.get().strip()
        preco = self.e_preco.get().strip()

        if not all([nome, cat, qtd, preco_compra, preco]):
            self.lbl_erro.config(text="Preencha todos os campos obrigatorios.")
            return

        try:
            qtd = int(qtd)
            preco_compra = float(preco_compra.replace(",", "."))
            preco = float(preco.replace(",", "."))
        except ValueError:
            self.lbl_erro.config(text="Quantidade deve ser inteiro e precos devem ser numeros.")
            return

        if qtd < 0 or preco_compra < 0 or preco < 0:
            self.lbl_erro.config(text="Quantidade e precos nao podem ser negativos.")
            return

        dados = {
            "nome": nome, "categoria": cat, "quantidade": qtd,
            "preco_compra": preco_compra, "preco": preco
        }
        if self.produto:
            dados["situacao"] = self.situacao_var.get()

        self.destroy()
        self.callback(dados)


class RelatorioLucros(tk.Toplevel):
    """Mostra o lucro calculado pelas saidas registradas."""

    def __init__(self, parent, categoria=None):
        super().__init__(parent)
        self.title("Relatorio de Lucros")
        self.geometry("880x520")
        self.configure(bg=CORES["fundo"])
        self.grab_set()
        self.categoria = categoria
        self._construir_ui()

    def _construir_ui(self):
        titulo = "Relatorio de Lucros"
        if self.categoria:
            titulo += f" - Categoria: {self.categoria}"
        tk.Label(self, text=titulo, font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(anchor="w", padx=20, pady=(16, 10))

        colunas = ("Produto", "Categoria", "Vendidos", "Custo", "Venda", "Lucro")
        tabela = ttk.Treeview(self, columns=colunas, show="headings", height=14)
        larguras = {
            "Produto": 220, "Categoria": 140, "Vendidos": 90,
            "Custo": 120, "Venda": 120, "Lucro": 120
        }
        for col in colunas:
            tabela.heading(col, text=col)
            tabela.column(col, width=larguras[col], anchor="center")
        tabela.pack(fill="both", expand=True, padx=20)

        total_custo = 0
        total_venda = 0
        total_lucro = 0
        for item in relatorio_lucros(self.categoria):
            total_custo += item["total_compra"]
            total_venda += item["total_venda"]
            total_lucro += item["lucro"]
            tabela.insert("", "end", values=(
                item["nome"], item["categoria"], item["quantidade_vendida"],
                f"R$ {item['total_compra']:.2f}",
                f"R$ {item['total_venda']:.2f}",
                f"R$ {item['lucro']:.2f}"
            ))

        resumo = (
            f"Custo total: R$ {total_custo:.2f}   |   "
            f"Venda total: R$ {total_venda:.2f}   |   "
            f"Lucro total: R$ {total_lucro:.2f}"
        )
        tk.Label(self, text=resumo, font=("Segoe UI", 12, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(anchor="e", padx=20, pady=14)


class RelatorioSaidas(tk.Toplevel):
    """Mostra todas as saidas/vendas registradas."""

    def __init__(self, parent, categoria=None):
        super().__init__(parent)
        self.title("Relatorio de Saidas")
        self.geometry("1080x540")
        self.configure(bg=CORES["fundo"])
        self.grab_set()
        self.categoria = categoria
        self._construir_ui()

    def _construir_ui(self):
        titulo = "Relatorio de Saidas"
        if self.categoria:
            titulo += f" - Categoria: {self.categoria}"
        tk.Label(self, text=titulo, font=("Segoe UI", 14, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(anchor="w", padx=20, pady=(16, 10))

        colunas = ("Data", "Produto", "Categoria", "Vendedor", "Qtd", "Status", "Compra", "Venda", "Lucro")
        tabela = ttk.Treeview(self, columns=colunas, show="headings", height=15)
        larguras = {
            "Data": 145, "Produto": 220, "Categoria": 130, "Vendedor": 160,
            "Qtd": 70, "Status": 100, "Compra": 100, "Venda": 100, "Lucro": 100
        }
        for col in colunas:
            tabela.heading(col, text=col)
            tabela.column(col, width=larguras[col], anchor="center")
        tabela.pack(fill="both", expand=True, padx=20)

        total_venda = 0
        total_lucro = 0
        for saida in listar_saidas(self.categoria):
            total_venda += saida["total_venda"]
            total_lucro += saida["lucro"]
            tabela.insert("", "end", values=(
                saida["data_venda"], saida["produto"], saida["categoria"],
                saida["vendedor"], saida["quantidade"], saida["status"].capitalize(),
                f"R$ {saida['preco_compra']:.2f}",
                f"R$ {saida['preco_venda']:.2f}",
                f"R$ {saida['lucro']:.2f}"
            ))

        resumo = (
            f"Total em vendas registradas: R$ {total_venda:.2f}   |   "
            f"Lucro total: R$ {total_lucro:.2f}"
        )
        tk.Label(self, text=resumo, font=("Segoe UI", 12, "bold"),
                 bg=CORES["fundo"], fg=CORES["texto"]).pack(anchor="e", padx=20, pady=14)
