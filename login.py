import tkinter as tk
from tkinter import messagebox
import sys
import os

# Garante que o Python encontre os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from usuario import autenticar_usuario


# ──────────────────────────────────────────────
#  Paleta de cores do sistema
# ──────────────────────────────────────────────
CORES = {
    "fundo":       "#1E1E2E",   # fundo escuro principal
    "painel":      "#2A2A3E",   # card/painel
    "primaria":    "#7C3AED",   # roxo (botão principal)
    "primaria_h":  "#6D28D9",   # roxo hover
    "texto":       "#F1F5F9",   # texto claro
    "texto_sub":   "#94A3B8",   # texto secundário
    "campo":       "#1E1E2E",   # fundo dos campos
    "borda":       "#3F3F5F",   # borda dos campos
    "erro":        "#EF4444",   # vermelho para erros
    "sucesso":     "#22C55E",   # verde para sucesso
}


class TelaLogin(tk.Tk):
    """
    Janela principal de login do sistema PDV.
    Após autenticação, redireciona para a tela correta
    com base no perfil do usuário (vendedor ou gerente).
    """

    def __init__(self):
        super().__init__()
        self.title("PDV Estoque — Login")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self._centralizar_janela(420, 520)
        self._construir_ui()

    # ── Utilitários ──────────────────────────
    def _centralizar_janela(self, largura, altura):
        """Posiciona a janela no centro da tela."""
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    # ── Construção da Interface ───────────────
    def _construir_ui(self):
        # Container principal com padding
        container = tk.Frame(self, bg=CORES["fundo"], padx=40, pady=40)
        container.pack(fill="both", expand=True)

        # ── Logo / Ícone ──
        logo_frame = tk.Frame(container, bg=CORES["primaria"],
                              width=72, height=72)
        logo_frame.pack(pady=(0, 20))
        logo_frame.pack_propagate(False)
        tk.Label(
            logo_frame, text="🏪", font=("Segoe UI Emoji", 30),
            bg=CORES["primaria"], fg=CORES["texto"]
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ── Título ──
        tk.Label(
            container, text="PDV Estoque",
            font=("Segoe UI", 22, "bold"),
            bg=CORES["fundo"], fg=CORES["texto"]
        ).pack()

        tk.Label(
            container, text="Faça login para continuar",
            font=("Segoe UI", 11),
            bg=CORES["fundo"], fg=CORES["texto_sub"]
        ).pack(pady=(4, 28))

        # ── Campo: Login ──
        self._label_campo(container, "Usuário")
        self.entry_login = self._entry(container)
        self.entry_login.focus()

        # ── Campo: Senha ──
        self._label_campo(container, "Senha")
        self.entry_senha = self._entry(container, senha=True)

        # Mensagem de erro (oculta por padrão)
        self.lbl_erro = tk.Label(
            container, text="", font=("Segoe UI", 10),
            bg=CORES["fundo"], fg=CORES["erro"]
        )
        self.lbl_erro.pack(pady=(8, 0))

        # ── Botão Entrar ──
        self.btn_entrar = tk.Button(
            container,
            text="Entrar",
            font=("Segoe UI", 12, "bold"),
            bg=CORES["primaria"],
            fg=CORES["texto"],
            activebackground=CORES["primaria_h"],
            activeforeground=CORES["texto"],
            relief="flat",
            cursor="hand2",
            command=self._fazer_login
        )
        self.btn_entrar.pack(fill="x", ipady=10, pady=(16, 0))

        # Hover no botão
        self.btn_entrar.bind("<Enter>", lambda e: self.btn_entrar.config(bg=CORES["primaria_h"]))
        self.btn_entrar.bind("<Leave>", lambda e: self.btn_entrar.config(bg=CORES["primaria"]))

        # Enter também dispara o login
        self.entry_senha.bind("<Return>", lambda e: self._fazer_login())
        self.entry_login.bind("<Return>", lambda e: self.entry_senha.focus())

        # ── Rodapé ──
        tk.Label(
            container,
            text="Credenciais padrão: gerente/1234 • vendedor/1234",
            font=("Segoe UI", 9), bg=CORES["fundo"], fg=CORES["texto_sub"]
        ).pack(side="bottom", pady=(20, 0))

    def _label_campo(self, parent, texto):
        tk.Label(
            parent, text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=CORES["fundo"], fg=CORES["texto_sub"],
            anchor="w"
        ).pack(fill="x")

    def _entry(self, parent, senha=False):
        frame = tk.Frame(parent, bg=CORES["borda"], padx=1, pady=1)
        frame.pack(fill="x", pady=(4, 12))

        entry = tk.Entry(
            frame,
            font=("Segoe UI", 12),
            bg=CORES["campo"],
            fg=CORES["texto"],
            insertbackground=CORES["texto"],
            relief="flat",
            show="●" if senha else ""
        )
        entry.pack(fill="x", ipady=8, padx=8)

        # Destaque de foco
        def on_focus_in(e):
            frame.config(bg=CORES["primaria"])

        def on_focus_out(e):
            frame.config(bg=CORES["borda"])

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        return entry

    # ── Lógica de Login ───────────────────────
    def _fazer_login(self):
        login = self.entry_login.get().strip()
        senha = self.entry_senha.get().strip()

        if not login or not senha:
            self._mostrar_erro("Preencha todos os campos.")
            return

        self.btn_entrar.config(text="Entrando...", state="disabled")
        self.update()

        usuario = autenticar_usuario(login, senha)

        if usuario:
            self._abrir_painel(usuario)
        else:
            self._mostrar_erro("Usuário ou senha incorretos.")
            self.btn_entrar.config(text="Entrar", state="normal")
            self.entry_senha.delete(0, "end")
            self.entry_senha.focus()

    def _mostrar_erro(self, mensagem):
        self.lbl_erro.config(text=f"⚠ {mensagem}")

    def _abrir_painel(self, usuario):
        """Fecha o login e abre o painel correto conforme o perfil."""
        self.destroy()

        if usuario["perfil"] == "gerente":
            from gerente import TelaGerente
            TelaGerente(usuario).mainloop()
        else:
            from vendedor import TelaVendedor
            TelaVendedor(usuario).mainloop()