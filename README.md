# ⚡ Gerenciador de Comandos Multi-Terminal

> Aplicativo desktop em Python que permite cadastrar, organizar e executar comandos em diferentes ferramentas (PowerShell, CMD, Bash, Python, Node.js, executáveis) com suporte a **inicialização automática com o sistema operacional** e **execução como administrador**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 👨‍💻 Desenvolvedor

**Taylor Reis**

- 🔗 GitHub: [@taylorreis](https://github.com/TaylorReis-lab)
- 💼 Projeto desenvolvido para automatizar tarefas repetitivas via comandos multi-terminal

---

## 📌 Sobre o Projeto

O **Gerenciador de Comandos Multi-Terminal** é uma aplicação desktop com interface gráfica (Tkinter) que resolve um problema comum: **executar comandos diferentes em ferramentas diferentes sem precisar abrir vários terminais manualmente**.

Com ele você pode:

- ✅ Cadastrar comandos com **nome amigável** e **descrição**
- ✅ Escolher qual **ferramenta** vai executar (PowerShell, CMD, Bash/WSL, Python, Node.js, executável direto)
- ✅ Usar **exemplos pré-configurados** para cada ferramenta
- ✅ Executar comandos **como administrador** (Windows `RunAs`)
- ✅ Marcar comandos para **iniciar junto com o sistema operacional**
- ✅ Receber **pedido de permissão explícito** antes de registrar na inicialização
- ✅ Persistir tudo em um arquivo **JSON** local

---

## 🖼️ Ferramentas Suportadas

| Ícone | Ferramenta | Como executa | Exemplo |
|-------|-----------|--------------|---------|
| 🔷 | **PowerShell** | `powershell -NoProfile -Command "..."` | `Get-Process` |
| ⬛ | **CMD (Prompt)** | `cmd /c ...` | `dir`, `systeminfo` |
| 🐧 | **Bash (WSL/Git Bash)** | `bash -c "..."` | `ls -la` |
| 🐍 | **Python** | `python -c "..."` | `print('Olá')` |
| 📄 | **Python (.py)** | `python arquivo.py` | `C:\scripts\app.py` |
| 🟢 | **Node.js** | `node -e "..."` | `console.log(1)` |
| ⚙️ | **Executável direto** | Roda direto | `calc.exe`, `notepad.exe` |

Cada ferramenta vem com **exemplos prontos** acessíveis pelo botão **"📋 Inserir exemplo da ferramenta"**.

---

## 🚀 Como Usar

### 1. Pré-requisitos

- Python **3.8+** instalado
- Tkinter (já incluso na instalação padrão do Python)
- Opcional: PowerShell, WSL/Bash, Node.js — dependendo das ferramentas que for usar

### 2. Executar o aplicativo

```bash
python gerenciador_comandos.py