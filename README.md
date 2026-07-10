# ZYRON

ZYRON é um assistente virtual local em Python preparado para crescer com Clean Architecture, SOLID, POO, injeção de dependência e plugins descobertos automaticamente.

## Arquitetura

```text
ZYRON/
├── main.py
├── domain/              # Entidades, Value Objects, contratos centrais e modelos
├── application/         # Casos de uso, pipeline, contexto, memória, eventos e scheduler
├── infrastructure/      # Persistência SQLite e adapters concretos
├── interfaces/          # Pontos de entrada futuros (CLI/API/voz/UI)
├── plugins/             # Plugins independentes auto-descobertos
│   ├── core/            # Memory, Browser, System, Application, AI
│   ├── integrations/    # Spotify, Gmail, GitHub, Calendar, Notion, Discord etc.
│   └── local/           # Arquivos, terminal, processos, volume, CPU, RAM etc.
├── config/              # Configurações futuras e exemplos
├── tests/               # Testes automatizados
├── core/, commands/     # Wrappers de compatibilidade legada
└── README.md
```

## Pipeline de comandos

Todo comando passa pelo mesmo fluxo profissional:

```text
Entrada
↓
IntentMatcher / SkillMatcher
↓
CommandProcessor
↓
PluginRegistry
↓
Plugin
↓
Resposta
↓
Histórico SQLite
↓
ConversationContext
↓
MemoryService / MemoryRepository
```

O roteamento usa objetos pequenos e coesos, sem `if` gigantes. Quando a confiança do matcher é baixa, a intenção cai para `AI_CHAT`, deixando o projeto preparado para Ollama sem depender de OpenAI.

## Plugins

Cada plugin expõe:

- `metadata` com `name`, `description`, `version` e `author`.
- `skills()` com palavras-chave, sinônimos, exemplos e capacidades.
- `can_handle()` para decidir se executa uma intenção.
- `execute()` para retornar uma resposta segura.

Os plugins são encontrados automaticamente por `PluginLoader` através de fábricas `create_plugin()`. Novos plugins devem ser independentes, não salvar tokens no código e responder amigavelmente quando credenciais de `.env` estiverem ausentes.

### Plugins existentes

- Core: Memory, Browser, System, Application e AI.
- Integrações preparadas: Spotify, Gmail, GitHub, Google Calendar, Notion, Discord, VSCode, Docker, Git, AWS, Browser, Windows, Linux, Terminal, Steam, OBS e YouTube.
- Locais: arquivos, pastas, terminal, processos, aplicativos, volume, brilho, bateria, CPU, RAM, disco e rede.

Comandos perigosos (excluir/mover arquivos, terminal, processos e ações de sistema) são modelados com capacidades perigosas e devem exigir confirmação antes de execução real.

## Memória

A memória possui duas camadas:

- Curto prazo: `ConversationContext`, com assunto ativo e histórico recente.
- Persistente: `MemoryRepository`/`MemoryService` usando SQLite.

Comandos suportados:

- `lembrar chave=valor`
- `consultar chave`
- `listar memórias`
- `esquecer chave`

A estrutura já está preparada para memória vetorial futura, sem embeddings nesta etapa.

## Configuração

Use `.env` para credenciais e opções:

```env
ZYRON_ASSISTANT_NAME=Zyron
ZYRON_OWNER_NAME=Leonidas
ZYRON_DATABASE_PATH=data/zyron.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OPENWEATHER_API_KEY=
```

Nunca salve tokens no código.

## Execução

```bash
pip install -r requirements-voice.txt
python main.py
```

O comando inicializa configurações, banco de dados, plugins, modelo Whisper, sintetizador TTS, verifica o microfone, fala `ZYRON online. Em que posso te ajudar?` e entra no loop principal de voz.

O modo texto permanece disponível separadamente para desenvolvimento, testes e depuração:

```bash
pip install -r requirements.txt
python -m interfaces.text_cli
```

Para testes rápidos do núcleo, use `ZyronApplication.process_text()`.

## Testes

```bash
pytest
```

## Dependências

As dependências comuns ficam em `requirements.txt`. Como `python main.py` inicia o modo voz, instale `requirements-voice.txt` para obter Whisper local, captura de microfone, TTS e reprodução de áudio. O modo texto usa apenas `requirements.txt` e não importa bibliotecas concretas de voz.

## Arquitetura consolidada

O ZYRON segue uma composição em camadas para manter baixo acoplamento e facilitar manutenção de longo prazo:

- `domain/`: modelos e portas centrais da aplicação.
- `application/`: casos de uso, contexto conversacional, memória, roteamento e matching de skills.
- `infrastructure/`: adapters concretos como SQLite e runtime de voz.
- `automation/`: gateways seguros para navegador e catálogo de aplicativos.
- `plugins/`: plugins declarativos que recebem dependências por injeção.
- `bootstrap/container.py`: composition root oficial; monta `Settings`, repositórios, serviços, registries, automação, voz e `CommandProcessor`.
- `interfaces/`: entrada por texto e voz.

## Fluxo de execução

1. A interface (`main.py`, `interfaces/voice_cli.py` ou `interfaces/text_cli.py`) cria o container.
2. O `CommandProcessor` recebe o texto do usuário.
3. O `SkillMatcher` escolhe uma skill com prioridade e confidence score.
4. O `CommandRouter` localiza o plugin responsável.
5. O plugin usa apenas dependências injetadas pelo container.
6. A interação é persistida e o `ConversationContext` é atualizado.

## Plugins e skills

Cada plugin possui metadados (`nome`, `descrição`, `versão`, `autor`, `capabilities`, `dependencies`, `state`) e declara suas skills. O `PluginRegistry` valida duplicidade e metadados mínimos. Falhas de carregamento são registradas em log sem impedir os demais plugins.

## Voz e modo texto

- Modo voz: `python main.py`
- Modo texto: `python -m interfaces.text_cli`

O loop de voz trata microfone ausente/ocupado, falhas de Whisper/TTS/pygame, silêncio, áudio vazio e wake word sem encerrar o processo por exceções transitórias.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-voice.txt
```

## Testes

```bash
python -m pytest
```

## Roadmap técnico

- Expandir providers externos por interfaces.
- Adicionar observabilidade estruturada.
- Evoluir o parser de memória por regras, mantendo opção sem IA.
- Separar plugins opcionais por pacotes instaláveis.
- Fortalecer testes de integração de voz em ambiente com hardware real.
