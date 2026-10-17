# ============================================================
# 🔥 COMMANDFORGE v1.3.0 - Gerenciador de Comandos Multi-Terminal
# Desenvolvedor: Taylor Reis
# GitHub: https://github.com/TaylorReis-lab
#
# Front-end: PyQt6 (responsivo, HiDPI, profissional)
# Compilação: pyinstaller --onefile --windowed --name CommandForge commandforge.py
# ============================================================

import subprocess
import sys


def instalar_dependencias():
    deps = {"PyQt6": "PyQt6", "pystray": "pystray", "PIL": "pillow"}
    faltando = []
    for mod, pacote in deps.items():
        try:
            __import__(mod)
        except ImportError:
            faltando.append(pacote)
    if not faltando:
        return
    print("=" * 60)
    print("🔧 CommandForge — Instalando dependências...")
    print(f"   Pacotes: {', '.join(faltando)}")
    print("=" * 60)
    for p in faltando:
        try:
            print(f"\n📦 Instalando '{p}'...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", p]
            )
            print(f"✅ '{p}' instalado!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Falha ao instalar '{p}': {e}")
    print("=" * 60 + "\n")


if __name__ == "__main__" and "--autostart" not in sys.argv:
    instalar_dependencias()

# ============================================================
# IMPORTS
# ============================================================
import json
import os
import platform
import threading
import time
import datetime
import webbrowser
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QObject, QThread, QSettings
from PyQt6.QtGui import (
    QFont,
    QIcon,
    QPixmap,
    QColor,
    QPainter,
    QBrush,
    QAction,
    QFontDatabase,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QFrame,
    QAbstractItemView,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QScrollArea,
    QGridLayout,
    QSpacerItem,
)

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
APP_VERSAO = "1.3.0"
DEV_NOME = "Taylor Reis"
DEV_GITHUB = "https://github.com/TaylorReis-lab"
REPO_URL = "https://github.com/TaylorReis-lab/ComandForge"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".commandforge.json")

# ============================================================
# FERRAMENTAS
# ============================================================
FERRAMENTAS = {
    "PowerShell": {
        "icone": "🔷",
        "descricao": "Shell avançado do Windows (.ps1)",
        "exec": ["powershell", "-NoProfile", "-Command"],
        "exemplos": [
            (
                "Listar processos",
                "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
            ),
            (
                "Info do sistema",
                "Get-ComputerInfo | Select-Object WindowsProductName, OsVersion",
            ),
            ("Listar serviços", "Get-Service | Where-Object {$_.Status -eq 'Running'}"),
            ("Desligar em 60s", "shutdown /s /t 60"),
            ("Abrir site", "Start-Process 'https://google.com'"),
        ],
        "obs": "Comandos nativos do PowerShell (Get-*, Set-*).",
    },
    "CMD (Prompt)": {
        "icone": "⬛",
        "descricao": "Prompt de comando clássico (.bat)",
        "exec": ["cmd", "/c"],
        "exemplos": [
            ("Listar arquivos", "dir"),
            ("Info do sistema", "systeminfo"),
            ("Abrir calculadora", "calc"),
            ("Abrir bloco de notas", "notepad"),
            ("Desligar em 60s", "shutdown /s /t 60"),
        ],
        "obs": "Comandos DOS clássicos.",
    },
    "Bash (WSL/Git Bash)": {
        "icone": "🐧",
        "descricao": "Shell Unix via WSL ou Git Bash",
        "exec": ["bash", "-c"],
        "exemplos": [
            ("Listar arquivos", "ls -la"),
            ("Info do sistema", "uname -a"),
            ("Espaço em disco", "df -h"),
            ("Ping google", "ping -c 4 google.com"),
        ],
        "obs": "Requer WSL ou Git Bash.",
    },
    "Python": {
        "icone": "🐍",
        "descricao": "Executa código Python inline",
        "exec": ["python", "-c"],
        "exemplos": [
            ("Hello World", "print('Ola Mundo!')"),
            ("Info Python", "import sys; print(sys.version)"),
            ("Listar arquivos", "import os; print(os.listdir('.'))"),
            ("Abrir site", "import webbrowser; webbrowser.open('https://google.com')"),
        ],
        "obs": "Código Python em uma linha.",
    },
    "Python (arquivo .py)": {
        "icone": "📄",
        "descricao": "Executa um arquivo .py",
        "exec": ["python"],
        "exemplos": [("Script exemplo", "C:\\scripts\\meu_script.py")],
        "obs": "Informe o caminho completo.",
    },
    "Node.js": {
        "icone": "🟢",
        "descricao": "JavaScript via Node.js",
        "exec": ["node", "-e"],
        "exemplos": [
            ("Hello World", "console.log('Ola Node!')"),
            ("Info Node", "console.log(process.version)"),
            (
                "Listar arquivos",
                "require('fs').readdirSync('.').forEach(f=>console.log(f))",
            ),
        ],
        "obs": "Requer Node.js.",
    },
    "Executável direto": {
        "icone": "⚙️",
        "descricao": "Executa .exe ou programa",
        "exec": [],
        "exemplos": [
            ("Calculadora", "calc.exe"),
            ("Bloco de notas", "notepad.exe"),
            ("Chrome", "chrome.exe"),
            ("Paint", "mspaint.exe"),
        ],
        "obs": "Nome ou caminho do executável.",
    },
}

# ============================================================
# QSS — ESTILO GLOBAL (CSS-like)
# ============================================================
QSS = """
QMainWindow, QDialog, QTabWidget::pane {
    background-color: #1e1e2e;
}
QWidget {
    color: #e4e8f5;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
}
QLabel { color: #e4e8f5; }
QLabel#titulo {
    font-size: 28px;
    font-weight: 700;
    color: #89b4fa;
}
QLabel#subtitulo {
    font-size: 13px;
    font-style: italic;
    color: #b8c0d8;
}
QLabel#secao {
    font-size: 18px;
    font-weight: 700;
    color: #e4e8f5;
}
QLabel#descricao {
    font-size: 13px;
    color: #b8c0d8;
}
QLabel#exemplos {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    color: #f9e2af;
}
QLabel#status_ok { font-size: 14px; font-weight: 700; color: #a6e3a1; }
QLabel#status_roda { font-size: 14px; font-weight: 700; color: #89b4fa; }
QLabel#status_err { font-size: 14px; font-weight: 700; color: #f38ba8; }

QFrame#card {
    background-color: #181825;
    border-radius: 12px;
}

QLineEdit {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 12px 14px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 15px;
    color: #e4e8f5;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QLineEdit:focus { border: 2px solid #89b4fa; }
QLineEdit::placeholder { color: #7f849c; }

QComboBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 15px;
    color: #e4e8f5;
    min-height: 28px;
}
QComboBox:focus { border: 2px solid #89b4fa; }
QComboBox::drop-down { border: none; width: 34px; }
QComboBox::down-arrow {
    image: none;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 10px solid #89b4fa;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    font-size: 14px;
    outline: 0;
}

QPushButton {
    background-color: #313244;
    border: none;
    border-radius: 10px;
    padding: 12px 22px;
    font-size: 15px;
    font-weight: 700;
    color: #1e1e2e;
    min-height: 28px;
}
QPushButton:hover { opacity: 0.85; }
QPushButton:pressed { padding-top: 13px; padding-bottom: 11px; }
QPushButton#primario   { background-color: #89b4fa; }
QPushButton#sucesso    { background-color: #a6e3a1; }
QPushButton#perigo     { background-color: #f38ba8; }
QPushButton#aviso      { background-color: #f9e2af; }
QPushButton#roxo       { background-color: #cba6f7; }
QPushButton#laranja    { background-color: #fab387; }
QPushButton#ciano      { background-color: #94e2d5; }
QPushButton#neutro     { background-color: #45475a; color: #e4e8f5; }

QCheckBox {
    font-size: 14px;
    color: #e4e8f5;
    spacing: 10px;
}
QCheckBox::indicator {
    width: 26px; height: 26px;
    border-radius: 6px;
    border: 2px solid #45475a;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border: 2px solid #89b4fa;
    image: none;
}

QTableWidget {
    background-color: #313244;
    alternate-background-color: #363a4f;
    gridline-color: #45475a;
    border-radius: 8px;
    font-size: 14px;
    color: #e4e8f5;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    outline: 0;
}
QTableWidget::item {
    padding: 10px 8px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QHeaderView::section {
    background-color: #45475a;
    color: #89b4fa;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 8px;
    border: none;
    border-right: 1px solid #313244;
}
QHeaderView::section:last { border-right: none; }

QTabWidget::pane {
    border: 2px solid #313244;
    border-radius: 10px;
    background-color: #11111b;
    top: -2px;
}
QTabBar::tab {
    background-color: #313244;
    color: #e4e8f5;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 14px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}

QTextEdit {
    background-color: #11111b;
    color: #a6e3a1;
    border: 2px solid #313244;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    padding: 8px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

QListWidget {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    color: #e4e8f5;
    padding: 6px;
    outline: 0;
}
QListWidget::item {
    padding: 10px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QScrollBar:vertical {
    background: #181825;
    width: 14px;
    border-radius: 7px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 7px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }

QScrollBar:horizontal {
    background: #181825;
    height: 14px;
    border-radius: 7px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 7px;
    min-width: 30px;
}

QMessageBox { background-color: #1e1e2e; }
QMessageBox QLabel { color: #e4e8f5; font-size: 14px; }
QMessageBox QPushButton { min-width: 100px; }

QSplitter::handle {
    background-color: #181825;
    width: 6px;
}
QSplitter::handle:hover { background-color: #89b4fa; }
"""


# ============================================================
# ESTRUTURAS DE DADOS
# ============================================================
@dataclass
class Execucao:
    exec_id: str
    nome: str
    ferramenta: str
    comando: str
    inicio: datetime.datetime
    proc: Optional[subprocess.Popen] = None
    tray: Optional[object] = None
    buffer: List[str] = field(default_factory=list)


# ============================================================
# JANELA DE LOGS (única, compacta, redimensionável)
# ============================================================
class JanelaLogs(QDialog):
    """Janela de logs única — nunca abre duplicada."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle(f"📜 {APP_NOME} — Logs")
        # 🔽 TAMANHO COMPACTO (antes era 1100x700)
        self.resize(820, 500)
        self.setMinimumSize(600, 380)
        self.setStyleSheet(QSS)
        # 🔽 Garante que só existe UMA instância
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setModal(False)

        self.abas: Dict[str, dict] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # ---- Header compacto ----
        header = QHBoxLayout()
        titulo = QLabel("📜 Logs em Tempo Real")
        titulo.setStyleSheet("font-size: 18px; font-weight: 700; color: #89b4fa;")
        header.addWidget(titulo)
        header.addStretch()

        btn_limpar = QPushButton("🧹 Limpar")
        btn_limpar.setObjectName("neutro")
        btn_limpar.setFixedHeight(32)
        btn_limpar.clicked.connect(self.limpar_aba_atual)
        header.addWidget(btn_limpar)

        btn_encerrar = QPushButton("❌ Encerrar")
        btn_encerrar.setObjectName("perigo")
        btn_encerrar.setFixedHeight(32)
        btn_encerrar.clicked.connect(self.encerrar_aba_atual)
        header.addWidget(btn_encerrar)
        layout.addLayout(header)

        # ---- Tabs ----
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._fechar_aba)
        layout.addWidget(self.tabs, 1)

        # Placeholder
        self._placeholder = QLabel(
            "Nenhuma execução ainda.\n\n"
            "Execute um comando no CommandForge\n"
            "para ver os logs em tempo real aqui."
        )
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("font-size: 14px; color: #b8c0d8;")
        layout.addWidget(self._placeholder, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(500)

    def _auto_refresh(self):
        try:
            self.atualizar_abas()
        except Exception:
            pass

    def adicionar_aba(self, execucao: Execucao):
        if execucao.exec_id in self.abas:
            return
        self._placeholder.hide()

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(6, 6, 6, 6)
        tab_layout.setSpacing(6)

        # Barra de status compacta
        barra = QHBoxLayout()
        lbl_info = QLabel(
            f"{execucao.ferramenta} • {execucao.inicio.strftime('%H:%M:%S')}"
        )
        lbl_info.setStyleSheet("font-size: 11px; color: #b8c0d8;")
        barra.addWidget(lbl_info)
        barra.addStretch()

        lbl_status = QLabel("● Rodando")
        lbl_status.setStyleSheet("font-size: 12px; font-weight: 700; color: #a6e3a1;")
        barra.addWidget(lbl_status)
        tab_layout.addLayout(barra)

        # Texto de log
        log = QTextEdit()
        log.setReadOnly(True)
        log.setStyleSheet(
            "background-color: #11111b; color: #a6e3a1; "
            "font-family: Consolas; font-size: 12px; "
            "border: 1px solid #313244; border-radius: 6px; padding: 6px;"
        )
        tab_layout.addWidget(log, 1)

        titulo_aba = f"{FERRAMENTAS.get(execucao.ferramenta, {}).get('icone', '⚙️')} {execucao.nome[:16]}"
        base = titulo_aba
        n = 2
        while self._find_tab_by_title(titulo_aba) is not None:
            titulo_aba = f"{base} ({n})"
            n += 1

        self.tabs.addTab(tab, titulo_aba)
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

        self.abas[execucao.exec_id] = {
            "tab": tab,
            "titulo": titulo_aba,
            "log": log,
            "lbl_status": lbl_status,
        }

    def _find_tab_by_title(self, titulo):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == titulo:
                return self.tabs.widget(i)
        return None

    def _fechar_aba(self, index):
        """Fecha a aba (não mata o processo)."""
        widget = self.tabs.widget(index)
        for eid, info in list(self.abas.items()):
            if info["tab"] == widget:
                del self.abas[eid]
                break
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self._placeholder.show()

    def escrever(self, exec_id, linha):
        info = self.abas.get(exec_id)
        if not info:
            return
        info["log"].append(linha)

    def marcar_terminado(self, exec_id, returncode):
        info = self.abas.get(exec_id)
        if not info:
            return
        if returncode == 0:
            info["lbl_status"].setText("✓ Finalizado (exit=0)")
            info["lbl_status"].setStyleSheet(
                "font-size: 12px; font-weight: 700; color: #a6e3a1;"
            )
        else:
            info["lbl_status"].setText(f"✗ Finalizado (exit={returncode})")
            info["lbl_status"].setStyleSheet(
                "font-size: 12px; font-weight: 700; color: #f38ba8;"
            )

    def limpar_aba_atual(self):
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        widget = self.tabs.widget(idx)
        for eid, info in self.abas.items():
            if info["tab"] == widget:
                info["log"].clear()
                return

    def encerrar_aba_atual(self):
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        widget = self.tabs.widget(idx)
        for eid, info in self.abas.items():
            if info["tab"] == widget:
                self.app._encerrar_execucao(eid)
                return

    def atualizar_abas(self):
        ativos = set(self.app.execucoes_ativas.keys())
        existentes = set(self.abas.keys())
        for eid in ativos - existentes:
            self.adicionar_aba(self.app.execucoes_ativas[eid])
        for eid in self.abas:
            info = self.app.execucoes_ativas.get(eid)
            if not info:
                continue
            log_atual = self.abas[eid]["log"].toPlainText()
            for linha in info.buffer:
                if linha not in log_atual:
                    self.abas[eid]["log"].append(linha)

    def closeEvent(self, event):
        """Ao fechar a janela, limpa a referência no app."""
        self.app.janela_logs = None
        event.accept()


# ============================================================
# APLICAÇÃO PRINCIPAL
# ============================================================
class CommandForge(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🔥 {APP_NOME} v{APP_VERSAO}")
        self.setMinimumSize(1000, 780)
        self.setStyleSheet(QSS)

        # 🔽 Tamanho configurável e persistente
        self.settings = QSettings("TaylorReis", "CommandForge")
        self._aplicar_tamanho_salvo()

        self.comandos: List[dict] = []
        self.execucoes_ativas: Dict[str, Execucao] = {}
        self.contador_exec = 0
        self.janela_logs: Optional[JanelaLogs] = None

        self.carregar_config()
        self.criar_interface()

    # ================= TAMANHO DA JANELA =================
    def _aplicar_tamanho_salvo(self):
        """Aplica tamanho salvo ou padrão confortável."""
        w = self.settings.value("janela/largura", 1100, type=int)
        h = self.settings.value("janela/altura", 820, type=int)
        x = self.settings.value("janela/x", -1, type=int)
        y = self.settings.value("janela/y", -1, type=int)

        # Limites de segurança
        w = max(1000, min(w, 1920))
        h = max(780, min(h, 1080))

        self.resize(w, h)
        if x >= 0 and y >= 0:
            self.move(x, y)
        else:
            self._centralizar()

    def _centralizar(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def closeEvent(self, event):
        # Salva tamanho e posição antes de fechar
        self.settings.setValue("janela/largura", self.width())
        self.settings.setValue("janela/altura", self.height())
        self.settings.setValue("janela/x", self.x())
        self.settings.setValue("janela/y", self.y())

        for exec_id in list(self.execucoes_ativas.keys()):
            execucao = self.execucoes_ativas.get(exec_id)
            if not execucao:
                continue
            try:
                if execucao.tray:
                    execucao.tray.stop()
            except Exception:
                pass
            try:
                if execucao.proc and execucao.proc.poll() is None:
                    execucao.proc.terminate()
            except Exception:
                pass
        self.execucoes_ativas.clear()
        event.accept()

        # ================= DIÁLOGO DE TAMANHO =================

    def abrir_dialogo_tamanho(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("📐 Tamanho da Janela")
        dlg.resize(500, 320)
        dlg.setStyleSheet(QSS)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)

        t = QLabel("Escolha o tamanho da aplicação")
        t.setObjectName("secao")
        lay.addWidget(t)

        # Presets
        presets_frame = QGridLayout()
        presets = [
            ("Compacto", 1000, 780),
            ("Padrão", 1100, 820),
            ("Grande", 1300, 920),
            ("Tela cheia", -1, -1),
        ]

        def aplicar_preset(w, h):
            if w == -1:
                self.showMaximized()
            else:
                self.showNormal()
                self.resize(w, h)
                self._centralizar()
            dlg.accept()

        for i, (nome, w, h) in enumerate(presets):
            b = QPushButton(
                f"{nome}\n{w if w > 0 else 'Tela cheia'} × {h if h > 0 else ''}".strip()
            )
            b.setMinimumHeight(60)
            if i == 0:
                b.setObjectName("sucesso")
            elif i == 1:
                b.setObjectName("primario")
            elif i == 2:
                b.setObjectName("roxo")
            else:
                b.setObjectName("ciano")
            b.clicked.connect(lambda _, w=w, h=h: aplicar_preset(w, h))
            presets_frame.addWidget(b, i // 2, i % 2)

        lay.addLayout(presets_frame)

        # Ajuste manual
        linha = QHBoxLayout()
        lbl_w = QLabel("Largura:")
        lbl_w.setStyleSheet("font-weight: 700;")
        linha.addWidget(lbl_w)

        spin_w = QLineEdit(str(self.width()))
        spin_w.setFixedWidth(90)
        linha.addWidget(spin_w)

        lbl_h = QLabel("Altura:")
        lbl_h.setStyleSheet("font-weight: 700;")
        linha.addWidget(lbl_h)

        spin_h = QLineEdit(str(self.height()))
        spin_h.setFixedWidth(90)
        linha.addWidget(spin_h)
        linha.addStretch()

        lay.addLayout(linha)

        def aplicar_manual():
            try:
                w = max(1000, min(int(spin_w.text()), 1920))
                h = max(780, min(int(spin_h.text()), 1080))
                self.showNormal()
                self.resize(w, h)
                self._centralizar()
                dlg.accept()
            except ValueError:
                QMessageBox.warning(dlg, "Aviso", "Digite números válidos.")

        btn = QPushButton("✅ Aplicar tamanho manual")
        btn.setObjectName("sucesso")
        btn.setMinimumHeight(42)
        btn.clicked.connect(aplicar_manual)
        lay.addWidget(btn)

        dlg.exec()

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

    # ================= UI =================
    def criar_interface(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        layout_principal.setSpacing(12)

        # ============ HEADER ============
        header = QFrame()
        header.setObjectName("card")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 12, 18, 12)

        logo = QLabel("🔥")
        logo.setStyleSheet("font-size: 40px;")
        header_layout.addWidget(logo)

        info_box = QVBoxLayout()
        info_box.setSpacing(0)
        titulo = QLabel(APP_NOME)
        titulo.setObjectName("titulo")
        info_box.addWidget(titulo)
        sub = QLabel(f"v{APP_VERSAO}  •  por {DEV_NOME}")
        sub.setObjectName("subtitulo")
        info_box.addWidget(sub)
        header_layout.addLayout(info_box)

        header_layout.addStretch()

        btn_tamanho = QPushButton("📐 Tamanho")
        btn_tamanho.setObjectName("neutro")
        btn_tamanho.setMinimumHeight(48)
        btn_tamanho.clicked.connect(self.abrir_dialogo_tamanho)
        header_layout.addWidget(btn_tamanho)

        btn_logs = QPushButton("📜 Logs em Tempo Real")
        btn_logs.setObjectName("ciano")
        btn_logs.setMinimumHeight(48)
        btn_logs.setMinimumWidth(220)
        btn_logs.clicked.connect(self.abrir_janela_logs)
        header_layout.addWidget(btn_logs)

        btn_gh = QPushButton("⭐ GitHub Dev")
        btn_gh.setObjectName("roxo")
        btn_gh.setMinimumHeight(48)
        btn_gh.clicked.connect(lambda: webbrowser.open(DEV_GITHUB))
        header_layout.addWidget(btn_gh)

        btn_repo = QPushButton("📦 Repositório")
        btn_repo.setObjectName("sucesso")
        btn_repo.setMinimumHeight(48)
        btn_repo.clicked.connect(lambda: webbrowser.open(REPO_URL))
        header_layout.addWidget(btn_repo)

        layout_principal.addWidget(header)

        # ============ SPLITTER (esquerda: config, direita: lista) ============
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        # ---- TOPO: Ferramenta + input ----
        topo = QWidget()
        topo_layout = QVBoxLayout(topo)
        topo_layout.setContentsMargins(0, 0, 0, 0)
        topo_layout.setSpacing(10)

        # Card ferramenta
        card_ferr = QFrame()
        card_ferr.setObjectName("card")
        cf_layout = QVBoxLayout(card_ferr)
        cf_layout.setContentsMargins(18, 14, 18, 14)
        cf_layout.setSpacing(10)

        lbl_f = QLabel("🔧 Ferramenta que executará o comando")
        lbl_f.setObjectName("secao")
        cf_layout.addWidget(lbl_f)

        linha_ferr = QHBoxLayout()
        self.combo_ferr = QComboBox()
        for k, v in FERRAMENTAS.items():
            self.combo_ferr.addItem(f"{v['icone']} {k}")
        self.combo_ferr.setMinimumWidth(280)
        self.combo_ferr.currentIndexChanged.connect(self.on_ferramenta_mudou)
        linha_ferr.addWidget(self.combo_ferr)

        self.lbl_desc_ferr = QLabel("")
        self.lbl_desc_ferr.setObjectName("descricao")
        linha_ferr.addWidget(self.lbl_desc_ferr, 1)
        cf_layout.addLayout(linha_ferr)

        self.lbl_exemplos = QLabel("")
        self.lbl_exemplos.setObjectName("exemplos")
        self.lbl_exemplos.setWordWrap(True)
        cf_layout.addWidget(self.lbl_exemplos)

        topo_layout.addWidget(card_ferr)

        # Card input
        card_input = QFrame()
        card_input.setObjectName("card")
        ci_layout = QVBoxLayout(card_input)
        ci_layout.setContentsMargins(18, 14, 18, 14)
        ci_layout.setSpacing(10)

        lbl_i = QLabel("📝 Novo comando")
        lbl_i.setObjectName("secao")
        ci_layout.addWidget(lbl_i)

        # Grid nome + comando
        grid = QGridLayout()
        grid.setVerticalSpacing(6)
        grid.setHorizontalSpacing(10)

        l1 = QLabel("Nome / Descrição:")
        l1.setStyleSheet("font-weight: 700; color: #b8c0d8;")
        grid.addWidget(l1, 0, 0)
        self.entry_nome = QLineEdit()
        self.entry_nome.setPlaceholderText("Ex: Listar processos")
        self.entry_nome.setMinimumHeight(46)
        grid.addWidget(self.entry_nome, 1, 0)

        l2 = QLabel("Comando:")
        l2.setStyleSheet("font-weight: 700; color: #b8c0d8;")
        grid.addWidget(l2, 2, 0)
        self.entry_comando = QLineEdit()
        self.entry_comando.setPlaceholderText(
            "Ex: Get-Process | Select-Object -First 5"
        )
        self.entry_comando.setMinimumHeight(46)
        grid.addWidget(self.entry_comando, 3, 0)

        ci_layout.addLayout(grid)

        # Linha de opções
        linha_opt = QHBoxLayout()
        btn_ex = QPushButton("📋 Inserir exemplo")
        btn_ex.setObjectName("aviso")
        btn_ex.setMinimumHeight(42)
        btn_ex.clicked.connect(self.mostrar_exemplos)
        linha_opt.addWidget(btn_ex)
        linha_opt.addStretch()

        self.chk_bandeja = QCheckBox("📥 Enviar terminal para a gaveta")
        self.chk_bandeja.setEnabled(PYSTRAY_OK)
        linha_opt.addWidget(self.chk_bandeja)

        ci_layout.addLayout(linha_opt)

        topo_layout.addWidget(card_input)

        # ---- Botões de ação ----
        linha_btns = QHBoxLayout()
        linha_btns.setSpacing(8)

        b_add = QPushButton("➕ Adicionar")
        b_add.setObjectName("sucesso")
        b_add.setMinimumHeight(48)
        b_add.clicked.connect(self.adicionar_comando)
        linha_btns.addWidget(b_add)

        b_exec = QPushButton("▶️ Executar")
        b_exec.setObjectName("primario")
        b_exec.setMinimumHeight(48)
        b_exec.clicked.connect(self.executar_selecionado)
        linha_btns.addWidget(b_exec)

        b_rem = QPushButton("🗑️ Remover")
        b_rem.setObjectName("perigo")
        b_rem.setMinimumHeight(48)
        b_rem.clicked.connect(self.remover_comando)
        linha_btns.addWidget(b_rem)

        b_auto = QPushButton("🔄 Auto-Start")
        b_auto.setObjectName("laranja")
        b_auto.setMinimumHeight(48)
        b_auto.clicked.connect(self.alternar_auto_start)
        linha_btns.addWidget(b_auto)

        b_band = QPushButton("📥 Gaveta ON/OFF")
        b_band.setObjectName("ciano")
        b_band.setMinimumHeight(48)
        b_band.clicked.connect(self.alternar_bandeja)
        linha_btns.addWidget(b_band)

        topo_layout.addLayout(linha_btns)
        splitter.addWidget(topo)

        # ---- BOTTOM: Lista ----
        card_lista = QFrame()
        card_lista.setObjectName("card")
        cl_layout = QVBoxLayout(card_lista)
        cl_layout.setContentsMargins(18, 14, 18, 14)
        cl_layout.setSpacing(10)

        header_lista = QHBoxLayout()
        lbl_lista = QLabel("📋 Comandos salvos")
        lbl_lista.setObjectName("secao")
        header_lista.addWidget(lbl_lista)

        self.lbl_contador = QLabel("0 comandos")
        self.lbl_contador.setObjectName("descricao")
        header_lista.addWidget(self.lbl_contador)
        header_lista.addStretch()
        cl_layout.addLayout(header_lista)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["Nome", "Ferramenta", "Comando", "Auto-Start", "Gaveta"]
        )
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.verticalHeader().setDefaultSectionSize(46)
        self.tabela.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Interactive
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabela.setColumnWidth(0, 200)
        self.tabela.itemSelectionChanged.connect(self.on_selecionar)
        self.tabela.doubleClicked.connect(lambda _: self.executar_selecionado())

        cl_layout.addWidget(self.tabela, 1)

        # ---- Rodapé da lista (inicialização) ----
        rodape = QHBoxLayout()
        rodape.setSpacing(8)

        b_init = QPushButton("🚀 Registrar na Inicialização")
        b_init.setObjectName("roxo")
        b_init.setMinimumHeight(46)
        b_init.clicked.connect(self.registrar_inicializacao)
        rodape.addWidget(b_init)

        b_rm = QPushButton("❌ Remover da Inicialização")
        b_rm.setObjectName("perigo")
        b_rm.setMinimumHeight(46)
        b_rm.clicked.connect(self.remover_inicializacao)
        rodape.addWidget(b_rm)

        rodape.addStretch()

        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("status_ok")
        rodape.addWidget(self.lbl_status)

        cl_layout.addLayout(rodape)

        splitter.addWidget(card_lista)
        splitter.setSizes([500, 350])

        layout_principal.addWidget(splitter, 1)

        # Estado inicial
        self.on_ferramenta_mudou()
        self.atualizar_lista()

    # ================= FERRAMENTA =================
    def ferramenta_atual(self):
        txt = self.combo_ferr.currentText()
        partes = txt.split(" ", 1)
        return partes[1] if len(partes) > 1 else txt

    def on_ferramenta_mudou(self):
        nome = self.ferramenta_atual()
        info = FERRAMENTAS.get(nome, {})
        self.lbl_desc_ferr.setText(info.get("descricao", ""))
        exemplos = info.get("exemplos", [])
        txt = ("  • " + "   |   ".join(n for n, _ in exemplos)) if exemplos else ""
        self.lbl_exemplos.setText(txt)

    def mostrar_exemplos(self):
        nome = self.ferramenta_atual()
        info = FERRAMENTAS.get(nome, {})
        exemplos = info.get("exemplos", [])
        if not exemplos:
            QMessageBox.information(self, "Exemplos", "Nenhum exemplo cadastrado.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Exemplos — {nome}")
        dlg.resize(800, 500)
        dlg.setStyleSheet(QSS)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        t = QLabel(f"{info.get('icone','')} Exemplos para {nome}")
        t.setObjectName("titulo")
        lay.addWidget(t)

        obs = QLabel(info.get("obs", ""))
        obs.setObjectName("exemplos")
        lay.addWidget(obs)

        lst = QListWidget()
        for n, c in exemplos:
            lst.addItem(QListWidgetItem(f"{n}  →  {c}"))
        lay.addWidget(lst, 1)

        btn = QPushButton("✅ Usar este exemplo")
        btn.setObjectName("sucesso")
        btn.setMinimumHeight(46)

        def usar():
            item = lst.currentItem()
            if not item:
                return
            idx = lst.row(item)
            n, c = exemplos[idx]
            self.entry_nome.setText(n)
            self.entry_comando.setText(c)
            dlg.accept()

        btn.clicked.connect(usar)
        lay.addWidget(btn)

        dlg.exec()

    # ================= CRUD =================
    def adicionar_comando(self):
        comando = self.entry_comando.text().strip()
        nome = self.entry_nome.text().strip() or comando
        ferramenta = self.ferramenta_atual()

        if not comando:
            QMessageBox.warning(self, "Aviso", "Digite um comando!")
            return

        self.comandos.append(
            {
                "nome": nome,
                "comando": comando,
                "ferramenta": ferramenta,
                "auto_start": False,
                "bandeja": self.chk_bandeja.isChecked() if PYSTRAY_OK else False,
            }
        )
        self.salvar_config()
        self.atualizar_lista()
        self.entry_comando.clear()
        self.entry_nome.clear()
        self._status(f"✅ Adicionado: {nome}")

    def remover_comando(self):
        idx = self.tabela.currentRow()
        if idx < 0 or idx >= len(self.comandos):
            QMessageBox.warning(self, "Aviso", "Selecione um comando!")
            return
        nome = self.comandos[idx]["nome"]
        resp = QMessageBox.question(
            self,
            "Confirmar",
            f"Remover '{nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            del self.comandos[idx]
            self.salvar_config()
            self.atualizar_lista()
            self._status(f"🗑️ Removido: {nome}")

    def on_selecionar(self):
        idx = self.tabela.currentRow()
        if idx < 0 or idx >= len(self.comandos):
            return
        c = self.comandos[idx]
        self.entry_nome.setText(c["nome"])
        self.entry_comando.setText(c["comando"])
        self.chk_bandeja.setChecked(c.get("bandeja", False))
        for i, (k, v) in enumerate(FERRAMENTAS.items()):
            if k == c.get("ferramenta", "PowerShell"):
                self.combo_ferr.setCurrentIndex(i)
                break

    def alternar_auto_start(self):
        idx = self.tabela.currentRow()
        if idx < 0 or idx >= len(self.comandos):
            QMessageBox.warning(self, "Aviso", "Selecione um comando!")
            return
        self.comandos[idx]["auto_start"] = not self.comandos[idx].get(
            "auto_start", False
        )
        self.salvar_config()
        self.atualizar_lista()
        estado = "ATIVADO ✅" if self.comandos[idx]["auto_start"] else "DESATIVADO ❌"
        self._status(f"Auto-start {estado}: {self.comandos[idx]['nome']}")

    def alternar_bandeja(self):
        if not PYSTRAY_OK:
            QMessageBox.warning(
                self,
                "Recurso indisponível",
                "Para usar a gaveta, instale:\n\npip install pystray pillow",
            )
            return
        idx = self.tabela.currentRow()
        if idx < 0 or idx >= len(self.comandos):
            QMessageBox.warning(self, "Aviso", "Selecione um comando!")
            return
        self.comandos[idx]["bandeja"] = not self.comandos[idx].get("bandeja", False)
        self.salvar_config()
        self.atualizar_lista()
        estado = "ATIVADO ✅" if self.comandos[idx]["bandeja"] else "DESATIVADO ❌"
        self._status(f"Gaveta {estado}: {self.comandos[idx]['nome']}")

    def atualizar_lista(self):
        self.tabela.setRowCount(len(self.comandos))
        for row, c in enumerate(self.comandos):
            ferr = c.get("ferramenta", "PowerShell")
            icone = FERRAMENTAS.get(ferr, {}).get("icone", "❔")
            auto = "✅" if c.get("auto_start") else "❌"
            band = "✅" if c.get("bandeja") else "❌"
            vals = [c["nome"], f"{icone} {ferr}", c["comando"], auto, band]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if col in (3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabela.setItem(row, col, item)

        total = len(self.comandos)
        self.lbl_contador.setText(f"{total} comando{'s' if total != 1 else ''}")

    def _status(self, texto):
        self.lbl_status.setText(texto)
        QTimer.singleShot(5000, lambda: self.lbl_status.setText(""))

    # ================= EXECUÇÃO =================
    def montar_cmd(self, comando, ferramenta):
        info = FERRAMENTAS.get(ferramenta, {})
        base = info.get("exec", [])
        if not base:
            return comando
        return base + [comando]

    def executar_selecionado(self):
        idx = self.tabela.currentRow()
        if idx < 0 or idx >= len(self.comandos):
            QMessageBox.warning(self, "Aviso", "Selecione um comando para executar!")
            return
        c = self.comandos[idx]

        resp = QMessageBox.question(
            self,
            "Executar como administrador?",
            f"Executar:\n\n"
            f"Ferramenta: {c.get('ferramenta','PowerShell')}\n"
            f"Comando: {c['comando']}\n\n"
            f"Deseja executar como ADMINISTRADOR?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        admin = resp == QMessageBox.StandardButton.Yes
        usar_bandeja = c.get("bandeja", False) and PYSTRAY_OK
        self.executar(
            c["comando"],
            c.get("ferramenta", "PowerShell"),
            admin=admin,
            minimizar_bandeja=usar_bandeja,
            nome=c["nome"],
        )

    def executar(
        self, comando, ferramenta, admin=False, minimizar_bandeja=False, nome=None
    ):
        nome = nome or comando[:30]

        self.contador_exec += 1
        exec_id = f"exec_{self.contador_exec}_{int(time.time())}"
        execucao = Execucao(
            exec_id=exec_id,
            nome=nome,
            ferramenta=ferramenta,
            comando=comando,
            inicio=datetime.datetime.now(),
        )
        self.execucoes_ativas[exec_id] = execucao

        if self.janela_logs is not None and self.janela_logs.isVisible():
            self.janela_logs.adicionar_aba(execucao)

        def run():
            try:
                # 🔐 Modo admin
                if admin and platform.system() == "Windows":
                    self._log_exec(
                        exec_id, f"[▶] Executando como ADMIN via {ferramenta}"
                    )
                    ps = (
                        f"Start-Process powershell -Verb RunAs "
                        f"-ArgumentList '-NoProfile','-Command','{comando}'"
                    )
                    proc = subprocess.Popen(
                        ["powershell", "-NoProfile", "-Command", ps], shell=True
                    )
                    execucao.proc = proc
                    self._log_exec(exec_id, "[⚠] UAC solicitado")
                    rc = proc.wait()
                    self._log_exec(
                        exec_id, f"[✓] Processo de elevação finalizado (exit={rc})"
                    )
                    self._finalizar_exec(exec_id, rc)
                    return

                # 📥 Modo gaveta
                if minimizar_bandeja and PYSTRAY_OK:
                    self._executar_na_gaveta(exec_id, comando, ferramenta, nome)
                    return

                # 🖥️ Modo terminal visível
                self._log_exec(exec_id, f"[▶] Executando via {ferramenta}")
                self._log_exec(exec_id, f"[cmd] {comando}")
                cmd = self.montar_cmd(comando, ferramenta)

                creationflags = 0
                if platform.system() == "Windows":
                    creationflags = subprocess.CREATE_NEW_CONSOLE

                if isinstance(cmd, list):
                    proc = subprocess.Popen(
                        cmd, shell=False, creationflags=creationflags
                    )
                else:
                    proc = subprocess.Popen(
                        cmd, shell=True, creationflags=creationflags
                    )

                execucao.proc = proc
                self._log_exec(exec_id, f"[🖥] Terminal aberto (PID {proc.pid})")
                self._log_exec(
                    exec_id, "[💡] Saída não capturada — terminal está visível"
                )

                rc = proc.wait()
                self._log_exec(exec_id, f"[✓] Finalizado (exit={rc})")
                self._finalizar_exec(exec_id, rc)

            except Exception as e:
                self._log_exec(exec_id, f"[ERRO] {e}")
                self._finalizar_exec(exec_id, -1)
                QTimer.singleShot(
                    0,
                    lambda: QMessageBox.critical(
                        self, "Erro", f"Falha ao executar:\n{e}"
                    ),
                )

        threading.Thread(target=run, daemon=True).start()

    def _executar_na_gaveta(self, exec_id, comando, ferramenta, nome):
        self._log_exec(exec_id, f"[📥] Executando na gaveta via {ferramenta}")
        self._log_exec(exec_id, f"[cmd] {comando}")
        cmd = self.montar_cmd(comando, ferramenta)

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
                    cmd,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    creationflags=creationflags,
                    startupinfo=startupinfo,
                )
            else:
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    creationflags=creationflags,
                    startupinfo=startupinfo,
                )
        except Exception as e:
            self._log_exec(exec_id, f"[ERRO] {e}")
            self._finalizar_exec(exec_id, -1)
            return

        execucao = self.execucoes_ativas[exec_id]
        execucao.proc = proc
        icone = self._criar_icone_execucao(exec_id, nome, ferramenta, proc)
        execucao.tray = icone
        self._log_exec(exec_id, f"[📥] Ícone adicionado na gaveta (PID {proc.pid})")

        def capturar():
            try:
                for linha in proc.stdout:
                    self._log_exec(exec_id, linha.rstrip())
                proc.wait()
                self._log_exec(exec_id, f"[✓] Finalizado (exit={proc.returncode})")
                self._finalizar_exec(exec_id, proc.returncode)
                self._remover_icone_gaveta(exec_id)
            except Exception as e:
                self._log_exec(exec_id, f"[ERRO captura] {e}")
                self._remover_icone_gaveta(exec_id)

        threading.Thread(target=capturar, daemon=True).start()

    def _log_exec(self, exec_id, linha):
        execucao = self.execucoes_ativas.get(exec_id)
        if execucao is None:
            return
        execucao.buffer.append(linha)

        def _ui():
            if self.janela_logs is not None and self.janela_logs.isVisible():
                self.janela_logs.escrever(exec_id, linha)

        QTimer.singleShot(0, _ui)

    def _finalizar_exec(self, exec_id, returncode):
        def _ui():
            if self.janela_logs is not None and self.janela_logs.isVisible():
                self.janela_logs.marcar_terminado(exec_id, returncode)
            nome = self.execucoes_ativas.get(
                exec_id, Execucao("", "?", "", "", datetime.datetime.now())
            ).nome
            self._status(f"✓ '{nome}' finalizado (exit={returncode})")

        QTimer.singleShot(0, _ui)

    def _encerrar_execucao(self, exec_id):
        execucao = self.execucoes_ativas.get(exec_id)
        if not execucao or execucao.proc is None:
            return
        try:
            execucao.proc.terminate()
            self._log_exec(exec_id, "[❌] Processo encerrado manualmente pelo usuário")
        except Exception as e:
            self._log_exec(exec_id, f"[ERRO ao encerrar] {e}")

    def _criar_icone_execucao(self, exec_id, nome, ferramenta, proc):
        icone_ferr = FERRAMENTAS.get(ferramenta, {}).get("icone", "⚙️")

        def mostrar(icon, item):
            QTimer.singleShot(0, lambda: self._info_execucao(exec_id))

        def matar(icon, item):
            self._encerrar_execucao(exec_id)

        menu = pystray.Menu(
            pystray.MenuItem(f"{icone_ferr} {nome}", None, enabled=False),
            pystray.MenuItem(f"🔧 {ferramenta}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("ℹ️ Info", mostrar, default=True),
            pystray.MenuItem("❌ Encerrar este comando", matar),
        )

        icone = pystray.Icon(
            exec_id, self._criar_imagem_icone(), f"{APP_NOME} — {nome}", menu
        )
        threading.Thread(target=icone.run, daemon=True).start()
        return icone

    def _criar_imagem_icone(self):
        img = Image.new("RGB", (64, 64), color="#1e1e2e")
        draw = ImageDraw.Draw(img)
        draw.ellipse((4, 4, 60, 60), fill="#89b4fa")
        draw.line((20, 22, 32, 32), fill="#1e1e2e", width=4)
        draw.line((32, 32, 20, 42), fill="#1e1e2e", width=4)
        draw.line((36, 44, 46, 44), fill="#1e1e2e", width=4)
        return img

    def _info_execucao(self, exec_id):
        execucao = self.execucoes_ativas.get(exec_id)
        if not execucao:
            return
        pid = execucao.proc.pid if execucao.proc else "N/A"
        status = (
            "em execução"
            if (execucao.proc and execucao.proc.poll() is None)
            else "finalizado"
        )
        QMessageBox.information(
            self,
            f"Execução — {execucao.nome}",
            f"Nome: {execucao.nome}\n"
            f"Ferramenta: {execucao.ferramenta}\n"
            f"Comando: {execucao.comando}\n"
            f"PID: {pid}\n"
            f"Status: {status}\n"
            f"Iniciado: {execucao.inicio.strftime('%H:%M:%S')}",
        )

    def _remover_icone_gaveta(self, exec_id):
        execucao = self.execucoes_ativas.get(exec_id)
        if not execucao or not execucao.tray:
            return
        try:
            execucao.tray.stop()
        except Exception:
            pass
        execucao.tray = None

    # ================= JANELA DE LOGS (ÚNICA) =================
    def abrir_janela_logs(self):
        # 🔒 Se já existe, apenas traz para frente
        if self.janela_logs is not None:
            try:
                if self.janela_logs.isVisible():
                    self.janela_logs.raise_()
                    self.janela_logs.activateWindow()
                    return
                else:
                    # Estava fechada, mas objeto existe — recria
                    self.janela_logs = None
            except RuntimeError:
                # Objeto foi destruído (WA_DeleteOnClose)
                self.janela_logs = None

        self.janela_logs = JanelaLogs(self, self)
        for eid, execucao in self.execucoes_ativas.items():
            self.janela_logs.adicionar_aba(execucao)
            for linha in execucao.buffer:
                self.janela_logs.escrever(eid, linha)
            if execucao.proc is not None and execucao.proc.poll() is not None:
                self.janela_logs.marcar_terminado(eid, execucao.proc.returncode)
        self.janela_logs.show()
        self.janela_logs.raise_()
        self.janela_logs.activateWindow()

    # ================= INICIALIZAÇÃO =================
    def obter_atalho_inicializacao(self):
        s = platform.system()
        if s == "Windows":
            pasta = os.path.join(
                os.getenv("APPDATA"),
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                "Startup",
            )
            return os.path.join(pasta, "CommandForge.bat")
        elif s == "Darwin":
            return os.path.expanduser(
                "~/Library/LaunchAgents/com.taylorreis.commandforge.plist"
            )
        else:
            return os.path.expanduser("~/.config/autostart/commandforge.desktop")

    def registrar_inicializacao(self):
        resp = QMessageBox.question(
            self,
            "🔐 Permissão Necessária",
            f"O {APP_NOME} precisa de permissão para:\n\n"
            "• Criar um atalho na pasta de inicialização do sistema\n"
            "• Executar automaticamente os comandos marcados como Auto-Start\n\n"
            "⚠️ Só marque comandos que você confia!\n\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        try:
            sistema = platform.system()
            # Quando compilado por PyInstaller, sys.executable é o .exe
            if getattr(sys, "frozen", False):
                caminho_app = sys.executable
            else:
                caminho_app = os.path.abspath(sys.argv[0])

            if sistema == "Windows":
                pasta = os.path.join(
                    os.getenv("APPDATA"),
                    "Microsoft",
                    "Windows",
                    "Start Menu",
                    "Programs",
                    "Startup",
                )
                os.makedirs(pasta, exist_ok=True)
                atalho = os.path.join(pasta, "CommandForge.bat")
                with open(atalho, "w", encoding="utf-8") as f:
                    if caminho_app.endswith(".py"):
                        f.write(f'@echo off\npythonw "{caminho_app}" --autostart\n')
                    else:
                        f.write(f'@echo off\nstart "" "{caminho_app}" --autostart\n')
                QMessageBox.information(self, "Sucesso", f"✅ Registrado!\n\n{atalho}")

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
                QMessageBox.information(
                    self, "Sucesso", "✅ Registrado na inicialização!"
                )

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
                QMessageBox.information(
                    self, "Sucesso", "✅ Registrado na inicialização!"
                )

            self._status("🚀 Registrado na inicialização do sistema")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao registrar:\n{e}")

    def remover_inicializacao(self):
        try:
            atalho = self.obter_atalho_inicializacao()
            if os.path.exists(atalho):
                os.remove(atalho)
                QMessageBox.information(
                    self, "Sucesso", "✅ Removido da inicialização!"
                )
                self._status("❌ Removido da inicialização")
            else:
                QMessageBox.information(
                    self, "Info", "Não está registrado na inicialização."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao remover:\n{e}")

    # ================= FINALIZAÇÃO =================
    def closeEvent(self, event):
        for exec_id in list(self.execucoes_ativas.keys()):
            execucao = self.execucoes_ativas.get(exec_id)
            if not execucao:
                continue
            try:
                if execucao.tray:
                    execucao.tray.stop()
            except Exception:
                pass
            try:
                if execucao.proc and execucao.proc.poll() is None:
                    execucao.proc.terminate()
            except Exception:
                pass
        self.execucoes_ativas.clear()
        event.accept()


# ============================================================
# EXECUÇÃO DOS COMANDOS AUTO-START
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

                creationflags = 0
                if platform.system() == "Windows":
                    creationflags = subprocess.CREATE_NO_WINDOW

                subprocess.Popen(
                    cmd, shell=isinstance(cmd, str), creationflags=creationflags
                )
                print(f"[auto-start] Executado: {c['nome']}")
            except Exception as e:
                print(f"Erro em '{c.get('nome')}': {e}")
    except Exception as e:
        print(f"Erro auto-start: {e}")


# ============================================================
# PONTO DE ENTRADA
# ============================================================
def main():
    if "--autostart" in sys.argv:
        executar_auto_start()
        sys.exit(0)

    # HiDPI / escalonamento (Windows)
    if platform.system() == "Windows":
        try:
            from PyQt6.QtCore import Qt as _Qt

            QApplication.setHighDpiScaleFactorRoundingPolicy(
                _Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NOME)
    app.setApplicationVersion(APP_VERSAO)
    app.setOrganizationName(DEV_NOME)

    # Fontes padrão grandes e legíveis
    try:
        QFontDatabase.addApplicationFont(":/fonts/SegoeUI.ttf")
    except Exception:
        pass
    f = QFont("Segoe UI", 12)
    app.setFont(f)

    win = CommandForge()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
