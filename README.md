# 🔥 CommandForge

> Gerenciador de comandos multi-terminal com inicialização automática, logs em tempo real, execução como administrador e envio do **terminal da ferramenta** para a **gaveta de execuções** (system tray).







**Desenvolvedor:** Taylor Reis  
**GitHub:** [github.com/TaylorReis-lab](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2FTaylorReis-lab)  
**Repositório:** [github.com/TaylorReis-lab/CommandForge](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2FTaylorReis-lab%2FCommandForge)

---

## 📌 Sobre o Projeto

O **CommandForge** é um aplicativo desktop em Python (Tkinter) que permite **cadastrar, organizar e executar comandos** em diferentes ferramentas (PowerShell, CMD, Bash/WSL, Python, Node.js ou executáveis diretos) — com suporte a:

- ✅ **Inicialização automática com o sistema operacional**
- ✅ **Execução como administrador** (UAC no Windows)
- ✅ **Envio do terminal para a gaveta de execuções** (system tray)
- ✅ **Logs em tempo real** capturados na interface
- ✅ **Instalação automática de dependências** na primeira execução

---

## ✨ Recursos

| Recurso | Descrição |
| :--- | :--- |
| 🔧 **Multi-terminal** | PowerShell, CMD, Bash/WSL, Python, Node.js, executável direto |
| 📋 **Exemplos pré-configurados** | Modelos prontos para cada ferramenta |
| 📥 **Gaveta individual** | Cada comando executado ganha seu próprio ícone na bandeja |
| 📜 **Painel de logs** | Saída em tempo real de cada execução |
| 🔐 **Permissão explícita** | Sempre pede confirmação antes de registrar na inicialização |
| ▶️ **Execução como admin** | Dispara UAC no Windows |
| ⭐ **Atalhos rápidos** | Botões para o GitHub do dev e do repositório |
| 💾 **Persistência JSON** | Comandos salvos em `~/.commandforge.json` |
| ⚙️ **Auto-instalação** | `pystray` e `pillow` são instalados automaticamente |
| 🔄 **Auto-Start por comando** | Marque individualmente quais comandos rodam no boot |

---

## 🖼️ Ferramentas Suportadas

| Ícone | Ferramenta | Como executa | Exemplo |
| :---: | :--- | :--- | :--- |
| 🔷 | **PowerShell** | `powershell -NoProfile -Command "..."` | `Get-Process` |
| ⬛ | **CMD (Prompt)** | `cmd /c ...` | `dir`, `systeminfo` |
| 🐧 | **Bash (WSL/Git Bash)** | `bash -c "..."` | `ls -la` |
| 🐍 | **Python** | `python -c "..."` | `print('Olá')` |
| 📄 | **Python (.py)** | `python arquivo.py` | `C:\scripts\app.py` |
| 🟢 | **Node.js** | `node -e "..."` | `console.log(1)` |
| ⚙️ | **Executável direto** | Roda direto | `calc.exe`, `notepad.exe` |

Cada ferramenta vem com **exemplos prontos** acessíveis pelo botão **"📋 Inserir exemplo da ferramenta"**.

---

## 🚀 Instalação

### Pré-requisitos

- Python **3.8+** instalado ([python.org](https://www.google.com/search?q=https%3A%2F%2Fwww.python.org%2Fdownloads%2F))
- Tkinter (já incluso na instalação padrão do Python)
- Opcional: PowerShell, WSL/Bash, Node.js — conforme as ferramentas que for usar

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/TaylorReis-lab/CommandForge.git
cd CommandForge

# 2. Execute — as dependências são instaladas automaticamente
python gerenciador_commandForge.pyw

# 3. Ou Execute com dois cliques — as dependências são instaladas automaticamente
("Dois cliques no executavel", gerenciador_commandForge.pyw)
```

> 💡 Na primeira execução, o app detecta e instala automaticamente `pystray` e `pillow` via `pip`. Se algo falhar (ex: sem internet), o app ainda abre, apenas com o recurso de gaveta desabilitado.

### Instalação manual das dependências (opcional)

```bash
pip install pystray pillow
```

---

## 🎯 Como Usar

### 1. Adicionar um comando

1. Escolha a ferramenta no dropdown (ex: 🔷 **PowerShell**)
2. *(Opcional)* Clique em **📋 Inserir exemplo da ferramenta** para pegar um modelo pronto
3. Preencha **Nome/Descrição** e o **Comando**
4. Marque **📥 Enviar terminal da ferramenta para a gaveta** *(opcional)*
5. Clique em **➕ Adicionar**

### 2. Executar um comando

1. Selecione o comando na lista
2. Clique em **▶️ Executar**
3. Confirme se deseja rodar como administrador

### 3. Configurar Auto-Start

1. Selecione o comando na lista
2. Clique em **🔄 Auto-Start** para alternar entre `✅ Sim` / `❌ Não`
3. Clique em **🚀 Registrar na Inicialização do Sistema**
4. ⚠️ Aceite a permissão na janela que aparecer

A partir do próximo boot, apenas os comandos marcados com ✅ serão executados automaticamente.

---

## 📥 Como Usar a Gaveta de Execuções

A **gaveta** é a bandeja do sistema (*system tray*) — canto inferior direito no Windows, barra superior no macOS/Linux.

### Por comando (permanente)

- Marque **"📥 Enviar terminal da ferramenta para a gaveta"** ao criar o comando
- Fica salvo como `"bandeja": true` no JSON
- Na execução, o processo roda oculto (sem janela piscando) e um ícone individual aparece na bandeja

### Botão manual

- **📥 Gaveta ON/OFF** — alterna a flag do comando selecionado na lista

---

## 🔐 Como funciona a permissão de inicialização

O aplicativo sempre pede confirmação explícita antes de criar qualquer atalho no sistema:

| Sistema | Local do registro | Arquivo criado |
| :--- | :--- | :--- |
| **Windows** | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` | `CommandForge.bat` |
| **Linux** | `~/.config/autostart/` | `commandforge.desktop` |
| **macOS** | `~/Library/LaunchAgents/` | `com.taylorreis.commandforge.plist` |

Para remover, basta clicar em **❌ Remover da Inicialização**.

---

## 🗂️ Estrutura do Projeto

```text
📁 CommandForge/
├── commandforge.py      # Aplicativo principal
├── README.md            # Este arquivo
└── LICENSE              # Licença MIT
```

Arquivo de configuração gerado em tempo de execução:

- `~/.commandforge.json`

---

## 🧠 Arquitetura

- `instalar_dependencias()` — bloco no topo que verifica e instala `pystray`/`pillow`
- `FERRAMENTAS` — dicionário de presets por ferramenta (comando base, exemplos, descrição)
- `CommandForge` — classe principal da UI (Tkinter) e lógica de CRUD
- `montar_cmd()` — monta a linha final de execução conforme a ferramenta escolhida
- `_executar_na_gaveta()` — executa o comando oculto e cria ícone individual na bandeja
- `_criar_icone_execucao()` — cria o ícone da gaveta com menu (Info / Encerrar)
- `executar_auto_start()` — roda no boot, lê o JSON e executa apenas comandos marcados
- **Execução em threads** — comandos não travam a interface

---

## 💡 Exemplos rápidos

```text
PowerShell  →  Get-Service | Where-Object {$_.Status -eq 'Running'}
CMD         →  systeminfo | findstr /C:"OS Name"
Bash        →  echo "Olá WSL!"
Python      →  import platform; print(platform.system())
Node.js     →  console.log('Olá Node!')
Executável  →  calc.exe
```

---

## ⚠️ Avisos de Segurança

- 🔒 Só adicione comandos que você confia — eles podem ser executados automaticamente no boot
- 🛡️ Alguns antivírus podem alertar sobre a escrita na pasta `Startup` — isso é esperado
- 🔑 O modo administrador usa `Start-Process -Verb RunAs` no Windows (UAC será exibido)
- 📝 O arquivo `~/.commandforge.json` armazena os comandos em texto plano — não guarde senhas nele
- 📥 Comandos na gaveta rodam ocultos — verifique o log na interface para acompanhar

---

## 🛠️ Tecnologias

- **Python 3** — linguagem principal
- **Tkinter / ttk** — interface gráfica
- **subprocess** — execução dos comandos
- **threading** — execução não-bloqueante
- **json** — persistência
- **platform** — detecção de SO
- **pystray + Pillow** — gaveta de execuções (system tray)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir *issues* ou enviar *pull requests* com melhorias, novas ferramentas ou correções.

```bash
# 1. Fork o projeto
# 2. Crie sua branch
git checkout -b feature/minha-feature

# 3. Commit suas mudanças
git commit -m "feat: adiciona nova ferramenta X"

# 4. Push
git push origin feature/minha-feature

# 5. Abra um Pull Request
```

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.

---

## 👤 Autor

**Taylor Reis**

- 🔗 GitHub: [@TaylorReis-lab](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2FTaylorReis-lab)
- 📦 Repositório: [CommandForge](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2FTaylorReis-lab%2FCommandForge)

Desenvolvido com foco em automação, produtividade e simplicidade no dia a dia.

⭐ **Se este projeto te ajudou, deixe uma estrela no repositório!**