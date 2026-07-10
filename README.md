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
python main.py
```

O comando inicializa o ZYRON, carrega plugins automaticamente e entra no loop de voz. Para testes rápidos do núcleo, use `ZyronApplication.process_text()`.

## Testes

```bash
pytest
```

## Dependências

As dependências estão em `requirements.txt`. O núcleo usa apenas biblioteca padrão e SQLite; voz, TTS, clima e IA local são adapters substituíveis.
