# ============================================================
# 🔥 COMMANDFORGE v1.2.0 - Gerenciador de Comandos Multi-Terminal
# Desenvolvedor: Taylor Reis
# GitHub: https://github.com/TaylorReis-lab
#
# INSTALAÇÃO AUTOMÁTICA DE DEPENDÊNCIAS
# Ao executar, o programa verifica e instala automaticamente:
#   - pystray  (ícone na gaveta/bandeja do sistema)
#   - pillow   (geração do ícone)
# ============================================================

import subprocess
import sys

def instalar_dependencias():
    """Verifica e instala dependências necessárias automaticamente."""
    dependencias = {
        "pystray": "pystray",
        "PIL": "pillow",
    }
    faltando = []
    for modulo, pacote in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(pacote)

    if not faltando:
        return

    print("=" * 60)
    print("🔧 CommandForge — Instalando dependências necessárias...")
    print(f"   Pacotes: {', '.join(faltando)}")
    print("=" * 60)

    for pacote in faltando:
        try:
            print(f"\n📦 Instalando '{pacote}'...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", pacote]
            )
            print(f"✅ '{pacote}' instalado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Falha ao instalar '{pacote}': {e}")
            print(f"   Tente manualmente: pip install {pacote}")

    print("\n" + "=" * 60)
    print("✅ Verificação de dependências concluída.")
    print("=" * 60 + "\n")


# Executa a verificação antes de qualquer import pesado
if __name__ == "__main__" and "--autostart" not in sys.argv:
    instalar_dependencias()


# ============================================================
# IMPORTS PRINCIPAIS
# ============================================================
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import platform
import webbrowser

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_OK = True
except ImportError:
    PYSTRAY_OK = False


# ============================================================
# CONSTANTES
# ============================================================
APP_NOME = "CommandForge"
APP_VERSAO = "1.2.0"
DEV_NOME = "Taylor Reis"
DEV_GITHUB = "https://github.com/TaylorReis-lab"
REPO_URL = "https://github.com/TaylorReis-lab/CommandForge"

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".commandforge.json")

FERRAMENTAS = {
    "PowerShell": {
        "icone": "🔷",
        "descricao": "Shell avançado do Windows com cmdlets (.ps1)",
        "exec": ["powershell", "-NoProfile", "-Command"],
        "exemplos": [
            ("Listar processos", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"),
            ("Info do sistema", "Get-ComputerInfo | Select-Object WindowsProductName, OsVersion"),
            ("Listar serviços", "Get-Service | Where-Object {$_.Status -eq 'Running'}"),
            ("Desligar em 60s", "shutdown /s /t 60"),
            ("Abrir site", "Start-Process 'https://google.com'"),
        ],
        "obs": "Use comandos nativos do PowerShell (Get-*, Set-*, etc).",
    },
    "CMD (Prompt)": {
        "icone": "⬛",
        "descricao": "Prompt de comando clássico do Windows (.bat)",
        "exec": ["cmd", "/c"],
        "exemplos": [
            ("Listar arquivos", "dir"),
            ("Info do sistema", "systeminfo"),
            ("Abrir calculadora", "calc"),
            ("Abrir bloco de notas", "notepad"),
            ("Desligar em 60s", "shutdown /s /t 60"),
        ],
        "obs": "Comandos DOS clássicos (dir, copy, move, etc).",
    },
    "Bash (WSL/Git Bash)": {
        "icone": "🐧",
        "descricao": "Shell Unix — funciona via WSL ou Git Bash",
        "exec": ["bash", "-c"],
        "exemplos": [
            ("Listar arquivos", "ls -la"),
            ("Info do sistema", "uname -a"),
            ("Espaço em disco", "df -h"),
            ("Ping google", "ping -c 4 google.com"),
        ],
        "obs": "Requer WSL ou Git Bash instalado no Windows.",
    },
    "Python": {
        "icone": "🐍",
        "descricao": "Executa scripts ou código Python diretamente",
        "exec": ["python", "-c"],
        "exemplos": [
            ("Hello World", "print('Ola Mundo!')"),
            ("Info Python", "import sys; print(sys.version)"),
            ("Listar arquivos", "import os; print(os.listdir('.'))"),
            ("Abrir site", "import webbrowser; webbrowser.open('https://google.com')"),
        ],
        "obs": "Use código Python válido em uma linha ou arquivo .py.",
    },
    "Python (arquivo .py)": {
        "icone": "📄",
        "descricao": "Executa um arquivo .py específico",
        "exec": ["python"],
        "exemplos": [("Script exemplo", "C:\\scripts\\meu_script.py")],
        "obs": "Informe o caminho completo do arquivo .py.",
    },
    "Node.js": {
        "icone": "🟢",
        "descricao": "Executa código JavaScript via Node.js",
        "exec": ["node", "-e"],
        "exemplos": [
            ("Hello World", "console.log('Ola Node!')"),
            ("Info Node", "console.log(process.version)"),
            ("Listar arquivos", "require('fs').readdirSync('.').forEach(f=>console.log(f))"),
        ],
        "obs": "Requer Node.js instalado (node --version).",
    },
    "Executável direto": {
        "icone": "⚙️",
        "descricao": "Executa um .exe ou programa diretamente",
        "exec": [],
        "exemplos": [
            ("Calculadora", "calc.exe"),
            ("Bloco de notas", "notepad.exe"),
            ("Chrome", "chrome.exe"),
            ("Paint", "mspaint.exe"),
        ],
        "obs": "Informe o nome ou caminho completo do executável.",
    },
}


class CommandForge:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🔥 {APP_NOME} v{APP_VERSAO} — Gerenciador de Comandos")
        self.root.geometry("1000x900")
        self.root.configure(bg="#1e1e2e")
        self.root.minsize(840, 740)

        self.comandos = []
        # Execuções ativas (para múltiplos terminais minimizados na gaveta)
        # id_exec -> {"tray": icon, "proc": Popen, "nome": str, "ferramenta": str}
        self.execucoes_ativas = {}
        self.contador_exec = 0

        self.carregar_config()
        self.criar_interface()

    # ================= CONFIG =================
    def carregar_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.comandos = json.load(f)
            except Exception:
                self.comandos = []

    def salvar_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.comandos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    # ================= INTERFACE =================
    def criar_interface(self):
        # ---- Cabeçalho ----
        frame_header = tk.Frame(self.root, bg="#181825")
        frame_header.pack(fill="x")

        tk.Label(
            frame_header, text=f"🔥 {APP_NOME}",
            font=("Segoe UI", 20, "bold"), bg="#181825", fg="#89b4fa"
        ).pack(side="left", padx=15, pady=10)

        tk.Label(
            frame_header, text=f"v{APP_VERSAO}  •  por {DEV_NOME}",
            font=("Segoe UI", 9, "italic"), bg="#181825", fg="#a6adc8"
        ).pack(side="left", pady=10)

        tk.Button(
            frame_header, text="⭐ GitHub Dev", bg="#cba6f7", fg="#1e1e2e",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            padx=10, pady=4, cursor="hand2",
            command=lambda: webbrowser.open(DEV_GITHUB)
        ).pack(side="right", padx=4, pady=10)

        tk.Button(
            frame_header, text="📦 Repositório", bg="#a6e3a1", fg="#1e1e2e",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            padx=10, pady=4, cursor="hand2",
            command=lambda: webbrowser.open(REPO_URL)
        ).pack(side="right", padx=4, pady=10)

        # ---- Ferramenta ----
        frame_ferr = tk.Frame(self.root, bg="#181825", bd=1, relief="solid")
        frame_ferr.pack(fill="x", padx=15, pady=8)

        tk.Label(
            frame_ferr, text="🔧 Ferramenta que executará o comando:",
            bg="#181825", fg="#cdd6f4", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(8, 4))

        linha_ferr = tk.Frame(frame_ferr, bg="#181825")
        linha_ferr.pack(fill="x", padx=10, pady=(0, 8))

        self.var_ferramenta = tk.StringVar(value="🔷 PowerShell")
        self.combo_ferr = ttk.Combobox(
            linha_ferr, textvariable=self.var_ferramenta,
            values=[f"{v['icone']} {k}" for k, v in FERRAMENTAS.items()],
            state="readonly", width=32, font=("Segoe UI", 10)
        )
        self.combo_ferr.pack(side="left")
        self.combo_ferr.bind("<<ComboboxSelected>>", self.on_ferramenta_mudou)

        self.lbl_desc_ferr = tk.Label(
            linha_ferr, text="", bg="#181825", fg="#a6adc8",
            font=("Segoe UI", 9, "italic")
        )
        self.lbl_desc_ferr.pack(side="left", padx=15)

        self.lbl_exemplos = tk.Label(
            frame_ferr, text="", bg="#181825", fg="#f9e2af",
            font=("Consolas", 9), justify="left", anchor="w"
        )
        self.lbl_exemplos.pack(fill="x", padx=10, pady=(0, 8))

        # ---- Entrada ----
        frame_input = tk.Frame(self.root, bg="#1e1e2e")
        frame_input.pack(fill="x", padx=15, pady=6)

        tk.Label(frame_input, text="Nome/Descrição:",
                 bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10)).pack(anchor="w")
        self.entry_nome = tk.Entry(
            frame_input, font=("Consolas", 11),
            bg="#313244", fg="#cdd6f4", insertbackground="white",
            relief="flat", bd=5
        )
        self.entry_nome.pack(fill="x", pady=(2, 6), ipady=4)

        tk.Label(frame_input, text="Comando:",
                 bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10)).pack(anchor="w")
        self.entry_comando = tk.Entry(
            frame_input, font=("Consolas", 11),
            bg="#313244", fg="#cdd6f4", insertbackground="white",
            relief="flat", bd=5
        )
        self.entry_comando.pack(fill="x", pady=(2, 6), ipady=4)

        # ---- Opções ----
        frame_opts = tk.Frame(frame_input, bg="#1e1e2e")
        frame_opts.pack(fill="x", pady=(0, 4))

        tk.Button(
            frame_opts, text="📋 Inserir exemplo da ferramenta",
            bg="#f9e2af", fg="#1e1e2e", font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=self.mostrar_exemplos
        ).pack(side="left")

        self.var_minimizar_bandeja = tk.BooleanVar(value=False)
        self.chk_bandeja = tk.Checkbutton(
            frame_opts, text="📥 Enviar terminal da ferramenta para a gaveta",
            variable=self.var_minimizar_bandeja,
            bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
            activebackground="#1e1e2e", activeforeground="#89b4fa",
            font=("Segoe UI", 9),
            state="normal" if PYSTRAY_OK else "disabled"
        )
        self.chk_bandeja.pack(side="right", padx=4)

        if not PYSTRAY_OK:
            tk.Label(
                frame_input,
                text="💡 Instale 'pystray' e 'pillow' para habilitar a gaveta:  pip install pystray pillow",
                bg="#1e1e2e", fg="#f9e2af", font=("Segoe UI", 8, "italic")
            ).pack(anchor="w")

        # ---- Botões ----
        frame_botoes = tk.Frame(self.root, bg="#1e1e2e")
        frame_botoes.pack(pady=6)

        self.criar_botao(frame_botoes, "➕ Adicionar", "#a6e3a1", self.adicionar_comando).pack(side="left", padx=4)
        self.criar_botao(frame_botoes, "▶️ Executar", "#89b4fa", self.executar_selecionado).pack(side="left", padx=4)
        self.criar_botao(frame_botoes, "🗑️ Remover", "#f38ba8", self.remover_comando).pack(side="left", padx=4)
        self.criar_botao(frame_botoes, "🔄 Auto-Start", "#fab387", self.alternar_auto_start).pack(side="left", padx=4)
        self.criar_botao(frame_botoes, "📥 Gaveta ON/OFF", "#94e2d5", self.alternar_bandeja).pack(side="left", padx=4)

        # ---- Lista ----
        frame_lista = tk.Frame(self.root, bg="#1e1e2e")
        frame_lista.pack(fill="both", expand=True, padx=15, pady=4)

        tk.Label(frame_lista, text="📋 Comandos salvos:",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        colunas = ("nome", "ferramenta", "comando", "auto", "bandeja")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=6)
        self.tree.heading("nome", text="Nome")
        self.tree.heading("ferramenta", text="Ferramenta")
        self.tree.heading("comando", text="Comando")
        self.tree.heading("auto", text="Auto-Start")
        self.tree.heading("bandeja", text="Gaveta")
        self.tree.column("nome", width=130)
        self.tree.column("ferramenta", width=110, anchor="center")
        self.tree.column("comando", width=400)
        self.tree.column("auto", width=80, anchor="center")
        self.tree.column("bandeja", width=70, anchor="center")

        sb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_selecionar)

        # ---- Logs ----
        frame_log = tk.Frame(self.root, bg="#1e1e2e")
        frame_log.pack(fill="both", expand=False, padx=15, pady=(4, 8))

        linha_log = tk.Frame(frame_log, bg="#1e1e2e")
        linha_log.pack(fill="x")
        tk.Label(linha_log, text="📜 Log de execução:",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Button(
            linha_log, text="🧹 Limpar log", bg="#6c7086", fg="#1e1e2e",
            font=("Segoe UI", 8, "bold"), relief="flat", bd=0,
            padx=8, pady=2, cursor="hand2",
            command=self.limpar_log
        ).pack(side="right")

        self.txt_log = scrolledtext.ScrolledText(
            frame_log, height=6, bg="#11111b", fg="#a6e3a1",
            font=("Consolas", 9), insertbackground="white",
            relief="flat", bd=0, wrap="word"
        )
        self.txt_log.pack(fill="both", expand=True, pady=(4, 0))
        self.txt_log.insert("end", f"[{APP_NOME}] Pronto para executar comandos...\n")
        self.txt_log.config(state="disabled")

        # ---- Rodapé ----
        frame_rod = tk.Frame(self.root, bg="#181825")
        frame_rod.pack(fill="x", padx=15, pady=8)

        self.criar_botao(
            frame_rod, "🚀 Registrar na Inicialização",
            "#cba6f7", self.registrar_inicializacao
        ).pack(side="left", padx=5)

        self.criar_botao(
            frame_rod, "❌ Remover da Inicialização",
            "#f38ba8", self.remover_inicializacao
        ).pack(side="left", padx=5)

        self.lbl_status = tk.Label(
            frame_rod, text="", bg="#181825", fg="#a6e3a1",
            font=("Segoe UI", 9, "italic")
        )
        self.lbl_status.pack(side="right", padx=10)

        self.on_ferramenta_mudou()
        self.atualizar_lista()

    def criar_botao(self, parent, texto, cor, comando):
        return tk.Button(
            parent, text=texto, bg=cor, fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"), relief="flat",
            bd=0, padx=14, pady=7, cursor="hand2",
            activebackground=cor, command=comando
        )

    # ================= LOG =================
    def log(self, msg):
        def _append():
            self.txt_log.config(state="normal")
            self.txt_log.insert("end", msg + "\n")
            self.txt_log.see("end")
            self.txt_log.config(state="disabled")
        self.root.after(0, _append)

    def limpar_log(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.config(state="disabled")
        self.log(f"[{APP_NOME}] Log limpo.")

    # ================= FERRAMENTA =================
    def ferramenta_atual(self):
        txt = self.var_ferramenta.get()
        partes = txt.split(" ", 1)
        return partes[1] if len(partes) > 1 else txt

    def on_ferramenta_mudou(self, event=None):
        nome = self.ferramenta_atual()
        info = FERRAMENTAS.get(nome, {})
        self.lbl_desc_ferr.config(text=info.get("descricao", ""))
        exemplos = info.get("exemplos", [])
        txt = ("  • " + "   |   ".join(n for n, _ in exemplos)) if exemplos else ""
        self.lbl_exemplos.config(text=txt)

    def mostrar_exemplos(self):
        nome = self.ferramenta_atual()
        info = FERRAMENTAS.get(nome, {})
        exemplos = info.get("exemplos", [])
        if not exemplos:
            messagebox.showinfo("Exemplos", "Nenhum exemplo cadastrado.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Exemplos — {nome}")
        win.geometry("640x400")
        win.configure(bg="#1e1e2e")

        tk.Label(win, text=f"{info.get('icone','')} Exemplos para {nome}",
                 bg="#1e1e2e", fg="#89b4fa",
                 font=("Segoe UI", 13, "bold")).pack(pady=10)

        tk.Label(win, text=info.get("obs", ""),
                 bg="#1e1e2e", fg="#f9e2af",
                 font=("Segoe UI", 9, "italic")).pack(pady=(0, 8))

        frame = tk.Frame(win, bg="#1e1e2e")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        lb = tk.Listbox(frame, bg="#313244", fg="#cdd6f4",
                        font=("Consolas", 10), selectbackground="#89b4fa",
                        selectforeground="#1e1e2e", bd=0)
        lb.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        for n, c in exemplos:
            lb.insert("end", f"{n}  →  {c}")

        def usar():
            sel = lb.curselection()
            if not sel:
                return
            n, c = exemplos[sel[0]]
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, n)
            self.entry_comando.delete(0, tk.END)
            self.entry_comando.insert(0, c)
            win.destroy()

        tk.Button(win, text="✅ Usar este exemplo", bg="#a6e3a1", fg="#1e1e2e",
                  font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                  padx=15, pady=6, cursor="hand2",
                  command=usar).pack(pady=10)

    # ================= CRUD =================
    def adicionar_comando(self):
        comando = self.entry_comando.get().strip()
        nome = self.entry_nome.get().strip() or comando
        ferramenta = self.ferramenta_atual()

        if not comando:
            messagebox.showwarning("Aviso", "Digite um comando!")
            return

        self.comandos.append({
            "nome": nome,
            "comando": comando,
            "ferramenta": ferramenta,
            "auto_start": False,
            "bandeja": self.var_minimizar_bandeja.get() if PYSTRAY_OK else False
        })
        self.salvar_config()
        self.atualizar_lista()
        self.entry_comando.delete(0, tk.END)
        self.entry_nome.delete(0, tk.END)
        self.lbl_status.config(text=f"✅ Adicionado: {nome}")
        self.log(f"[+] Comando adicionado: {nome} ({ferramenta})")

    def remover_comando(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um comando!")
            return
        idx = self.tree.index(sel[0])
        nome = self.comandos[idx]["nome"]
        if messagebox.askyesno("Confirmar", f"Remover '{nome}'?"):
            del self.comandos[idx]
            self.salvar_config()
            self.atualizar_lista()
            self.lbl_status.config(text=f"🗑️ Removido: {nome}")
            self.log(f"[-] Comando removido: {nome}")

    def on_selecionar(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        c = self.comandos[idx]
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, c["nome"])
        self.entry_comando.delete(0, tk.END)
        self.entry_comando.insert(0, c["comando"])
        self.var_minimizar_bandeja.set(c.get("bandeja", False))
        for k, v in FERRAMENTAS.items():
            if k == c.get("ferramenta", "PowerShell"):
                self.var_ferramenta.set(f"{v['icone']} {k}")
                self.on_ferramenta_mudou()
                break

    def alternar_auto_start(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um comando!")
            return
        idx = self.tree.index(sel[0])
        self.comandos[idx]["auto_start"] = not self.comandos[idx].get("auto_start", False)
        self.salvar_config()
        self.atualizar_lista()
        estado = "ATIVADO ✅" if self.comandos[idx]["auto_start"] else "DESATIVADO ❌"
        self.lbl_status.config(text=f"Auto-start {estado}: {self.comandos[idx]['nome']}")
        self.log(f"[auto] {self.comandos[idx]['nome']}: {estado}")

    def alternar_bandeja(self):
        if not PYSTRAY_OK:
            messagebox.showwarning(
                "Recurso indisponível",
                "Para usar a gaveta, instale:\n\npip install pystray pillow"
            )
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um comando!")
            return
        idx = self.tree.index(sel[0])
        self.comandos[idx]["bandeja"] = not self.comandos[idx].get("bandeja", False)
        self.salvar_config()
        self.atualizar_lista()
        estado = "ATIVADO ✅" if self.comandos[idx]["bandeja"] else "DESATIVADO ❌"
        self.lbl_status.config(text=f"Gaveta {estado}: {self.comandos[idx]['nome']}")
        self.log(f"[gaveta] {self.comandos[idx]['nome']}: {estado}")

    def atualizar_lista(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for c in self.comandos:
            ferr = c.get("ferramenta", "PowerShell")
            icone = FERRAMENTAS.get(ferr, {}).get("icone", "❔")
            auto = "✅" if c.get("auto_start") else "❌"
            band = "✅" if c.get("bandeja") else "❌"
            self.tree.insert("", "end", values=(
                c["nome"], f"{icone} {ferr}", c["comando"], auto, band
            ))

    # ================= EXECUÇÃO =================
    def montar_cmd(self, comando, ferramenta):
        info = FERRAMENTAS.get(ferramenta, {})
        base = info.get("exec", [])
        if not base:
            return comando
        return base + [comando]

    def executar_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um comando para executar!")
            return
        idx = self.tree.index(sel[0])
        c = self.comandos[idx]

        admin = messagebox.askyesno(
            "Executar como administrador?",
            f"Executar:\n\n"
            f"Ferramenta: {c.get('ferramenta','PowerShell')}\n"
            f"Comando: {c['comando']}\n\n"
            f"Deseja executar como ADMINISTRADOR?"
        )
        usar_bandeja = c.get("bandeja", False) and PYSTRAY_OK
        self.executar(c["comando"], c.get("ferramenta", "PowerShell"),
                      admin=admin, minimizar_bandeja=usar_bandeja,
                      nome=c["nome"])

    def executar(self, comando, ferramenta, admin=False,
                 minimizar_bandeja=False, nome=None):
        nome = nome or comando[:30]

        def run():
            try:
                # 🔐 Modo admin (PowerShell elevado) — janela visível sempre
                if admin and platform.system() == "Windows":
                    self.log(f"[▶] Executando como ADMIN via {ferramenta}: {comando}")
                    ps = (
                        f"Start-Process powershell -Verb RunAs "
                        f"-ArgumentList '-NoProfile','-Command','{comando}'"
                    )
                    subprocess.Popen(["powershell", "-NoProfile", "-Command", ps], shell=True)
                    self.log("[⚠] Executado como administrador (UAC solicitado)")
                    self.root.after(0, lambda: self.lbl_status.config(
                        text="▶️ Executado como ADMIN"))
                    return

                # 📥 Modo GAVETA: apenas o TERMINAL DA FERRAMENTA vai para a bandeja
                # O processo roda oculto + ícone individual na gaveta
                if minimizar_bandeja and PYSTRAY_OK:
                    self._executar_na_gaveta(comando, ferramenta, nome)
                    return

                # 🖥️ Modo terminal visível (janela do console aberta)
                self.log(f"[▶] Executando via {ferramenta}: {comando}")
                cmd = self.montar_cmd(comando, ferramenta)

                creationflags = 0
                if platform.system() == "Windows":
                    # Abre nova janela de console visível
                    creationflags = subprocess.CREATE_NEW_CONSOLE

                if isinstance(cmd, list):
                    proc = subprocess.Popen(
                        cmd, shell=False,
                        creationflags=creationflags
                    )
                else:
                    proc = subprocess.Popen(
                        cmd, shell=True,
                        creationflags=creationflags
                    )

                self.log(f"[🖥] Terminal iniciado (PID {proc.pid})")
                self.root.after(0, lambda: self.lbl_status.config(
                    text=f"▶️ Executado: {comando[:50]}"))

            except Exception as e:
                self.log(f"[ERRO] {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro", f"Falha ao executar:\n{e}"))

        threading.Thread(target=run, daemon=True).start()

    def _executar_na_gaveta(self, comando, ferramenta, nome):
        """Executa o comando oculto e adiciona um ícone individual na gaveta."""
        self.contador_exec += 1
        exec_id = f"exec_{self.contador_exec}_{int(time.time())}"

        self.log(f"[📥] Executando na gaveta: {nome} ({ferramenta})")
        cmd = self.montar_cmd(comando, ferramenta)

        # Configuração para rodar sem janela e capturar saída
        creationflags = 0
        startupinfo = None
        if platform.system() == "Windows":
            creationflags = subprocess.CREATE_NO_WINDOW
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        try:
            if isinstance(cmd, list):
                proc = subprocess.Popen(
                    cmd, shell=False,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="ignore",
                    creationflags=creationflags,
                    startupinfo=startupinfo
                )
            else:
                proc = subprocess.Popen(
                    cmd, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="ignore",
                    creationflags=creationflags,
                    startupinfo=startupinfo
                )
        except Exception as e:
            self.log(f"[ERRO] {e}")
            return
        # Cria ícone individual na bandeja para ESTE comando
        icone = self._criar_icone_execucao(exec_id, nome, ferramenta, proc)

        # Registra a execução ativa
        self.execucoes_ativas[exec_id] = {
            "tray": icone,
            "proc": proc,
            "nome": nome,
            "ferramenta": ferramenta,
            "comando": comando,
        }

        # Thread para capturar a saída em tempo real
        def capturar():
            try:
                for linha in proc.stdout: # type: ignore
                    self.log(f"[{ferramenta}] {linha.rstrip()}")
                proc.wait()
                self.log(f"[✓] '{nome}' finalizado (exit={proc.returncode})")
                # Remove o ícone da gaveta quando o processo termina
                self._remover_execucao(exec_id, aviso=False)
            except Exception as e:
                self.log(f"[ERRO captura] {e}")

        threading.Thread(target=capturar, daemon=True).start()

        self.root.after(0, lambda: self.lbl_status.config(
            text=f"📥 Executando na gaveta: {nome}"))

    def _criar_icone_execucao(self, exec_id, nome, ferramenta, proc):
        """Cria um ícone individual na gaveta para uma execução específica."""
        icone_ferr = FERRAMENTAS.get(ferramenta, {}).get("icone", "⚙️")

        def mostrar(icon, item):
            # Mostra uma janelinha com info da execução
            self.root.after(0, lambda: self._info_execucao(exec_id))

        def matar(icon, item):
            # Encerra o processo
            try:
                proc.terminate()
                self.log(f"[❌] Processo encerrado manualmente: {nome}")
            except Exception as e:
                self.log(f"[ERRO] {e}")
            self._remover_execucao(exec_id, aviso=True)

        menu = pystray.Menu(
            pystray.MenuItem(f"{icone_ferr} {nome}", None, enabled=False),
            pystray.MenuItem(f"🔧 {ferramenta}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("ℹ️ Info", mostrar, default=True),
            pystray.MenuItem("❌ Encerrar este comando", matar),
        )

        icone = pystray.Icon(
            exec_id,
            self._criar_imagem_icone(icone_ferr, cor="#89b4fa"),
            f"{APP_NOME} — {nome}",
            menu
        )

        threading.Thread(target=icone.run, daemon=True).start()
        return icone

    def _criar_imagem_icone(self, emoji, cor="#89b4fa"):
        """Gera uma imagem simples para o ícone (quadrado com a inicial)."""
        img = Image.new("RGB", (64, 64), color="#1e1e2e")
        draw = ImageDraw.Draw(img)
        draw.ellipse((4, 4, 60, 60), fill=cor)
        # Desenha ">" central como símbolo de terminal
        draw.line((20, 22, 32, 32), fill="#1e1e2e", width=4)
        draw.line((32, 32, 20, 42), fill="#1e1e2e", width=4)
        draw.line((36, 44, 46, 44), fill="#1e1e2e", width=4)
        return img

    def _info_execucao(self, exec_id):
        """Mostra info de uma execução na gaveta."""
        info = self.execucoes_ativas.get(exec_id)
        if not info:
            return
        messagebox.showinfo(
            f"Execução na gaveta — {info['nome']}",
            f"Nome: {info['nome']}\n"
            f"Ferramenta: {info['ferramenta']}\n"
            f"Comando: {info['comando']}\n"
            f"PID: {info['proc'].pid}\n"
            f"Status: {'em execução' if info['proc'].poll() is None else 'finalizado'}"
        )

    def _remover_execucao(self, exec_id, aviso=True):
        """Remove a execução da gaveta (chamado ao encerrar ou finalizar)."""
        info = self.execucoes_ativas.pop(exec_id, None)
        if not info:
            return
        try:
            info["tray"].stop()
        except Exception:
            pass
        if aviso:
            self.log(f"[📥] Removido da gaveta: {info['nome']}")

    # ================= INICIALIZAÇÃO DO SISTEMA =================
    def obter_atalho_inicializacao(self):
        s = platform.system()
        if s == "Windows":
            pasta = os.path.join(
                os.getenv("APPDATA"), "Microsoft", "Windows", # type: ignore
                "Start Menu", "Programs", "Startup"
            ) # type: ignore
            return os.path.join(pasta, "CommandForge.bat")
        elif s == "Darwin":
            return os.path.expanduser("~/Library/LaunchAgents/com.taylorreis.commandforge.plist")
        else:
            return os.path.expanduser("~/.config/autostart/commandforge.desktop")

    def registrar_inicializacao(self):
        resposta = messagebox.askyesno(
            "🔐 Permissão Necessária",
            f"O {APP_NOME} precisa de permissão para:\n\n"
            "• Criar um atalho na pasta de inicialização do sistema\n"
            "• Executar automaticamente os comandos marcados como Auto-Start\n\n"
            "⚠️ Só marque comandos que você confia!\n\n"
            "Deseja continuar?"
        )
        if not resposta:
            return

        try:
            sistema = platform.system()
            caminho_app = os.path.abspath(sys.argv[0])

            if sistema == "Windows":
                pasta = os.path.join(
                    os.getenv("APPDATA"), "Microsoft", "Windows", # type: ignore
                    "Start Menu", "Programs", "Startup"
                ) # type: ignore
                os.makedirs(pasta, exist_ok=True)
                atalho = os.path.join(pasta, "CommandForge.bat")

                with open(atalho, "w", encoding="utf-8") as f:
                    if caminho_app.endswith(".py"):
                        f.write(f'@echo off\npythonw "{caminho_app}" --autostart\n')
                    else:
                        f.write(f'@echo off\nstart "" "{caminho_app}" --autostart\n')

                messagebox.showinfo("Sucesso",
                    f"✅ Registrado na inicialização!\n\n{atalho}")
                self.log(f"[init] Registrado em: {atalho}")

            elif sistema == "Linux":
                pasta = os.path.expanduser("~/.config/autostart")
                os.makedirs(pasta, exist_ok=True)
                atalho = os.path.join(pasta, "commandforge.desktop")
                with open(atalho, "w", encoding="utf-8") as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Name=CommandForge
Comment=Gerenciador de Comandos por Taylor Reis
Exec={sys.executable} {caminho_app} --autostart
X-GNOME-Autostart-enabled=true
""")
                messagebox.showinfo("Sucesso", "✅ Registrado na inicialização!")
                self.log(f"[init] Registrado em: {atalho}")

            elif sistema == "Darwin":
                plist = self.obter_atalho_inicializacao()
                os.makedirs(os.path.dirname(plist), exist_ok=True)
                with open(plist, "w", encoding="utf-8") as f:
                    f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.taylorreis.commandforge</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{caminho_app}</string>
        <string>--autostart</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>""")
                messagebox.showinfo("Sucesso", "✅ Registrado na inicialização!")
                self.log(f"[init] Registrado em: {plist}")

            self.lbl_status.config(text="🚀 Registrado na inicialização do sistema")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar:\n{e}")
            self.log(f"[ERRO init] {e}")

    def remover_inicializacao(self):
        try:
            atalho = self.obter_atalho_inicializacao()
            if os.path.exists(atalho):
                os.remove(atalho)
                messagebox.showinfo("Sucesso", "✅ Removido da inicialização!")
                self.lbl_status.config(text="❌ Removido da inicialização")
                self.log(f"[init] Removido: {atalho}")
            else:
                messagebox.showinfo("Info", "Não está registrado na inicialização.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao remover:\n{e}")
            self.log(f"[ERRO init] {e}")

    # ================= FINALIZAÇÃO =================
    def on_close(self):
        """Encerra todos os ícones da gaveta ao fechar o app."""
        for exec_id in list(self.execucoes_ativas.keys()):
            info = self.execucoes_ativas.get(exec_id)
            if not info:
                continue
            try:
                info["tray"].stop()
            except Exception:
                pass
            try:
                if info["proc"].poll() is None:
                    info["proc"].terminate()
            except Exception:
                pass
        self.execucoes_ativas.clear()
        self.root.destroy()

# ============================================================
# EXECUÇÃO DOS COMANDOS AUTO-START (roda no boot)
# ============================================================
def executar_auto_start():
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            comandos = json.load(f)

        for c in comandos:
            if not c.get("auto_start"):
                continue
            try:
                ferr = c.get("ferramenta", "PowerShell")
                info = FERRAMENTAS.get(ferr, {})
                base = info.get("exec", [])
                cmd = (base + [c["comando"]]) if base else c["comando"]

                # Auto-start roda silencioso
                creationflags = 0
                if platform.system() == "Windows":
                    creationflags = subprocess.CREATE_NO_WINDOW

                subprocess.Popen(
                    cmd, shell=isinstance(cmd, str),
                    creationflags=creationflags
                )
                print(f"[auto-start] Executado: {c['nome']}")
            except Exception as e:
                print(f"Erro em '{c.get('nome')}': {e}")
    except Exception as e:
        print(f"Erro auto-start: {e}")

# ============================================================
# PONTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    # Modo auto-start: executa comandos marcados e sai (sem abrir UI)
    if "--autostart" in sys.argv:
        executar_auto_start()
        sys.exit(0)

    # Modo normal: abre a interface gráfica
    root = tk.Tk()
    app = CommandForge(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()