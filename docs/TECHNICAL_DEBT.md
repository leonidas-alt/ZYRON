# Dívida Técnica do ZYRON

Este documento centraliza débitos técnicos, melhorias pendentes, refatorações futuras, problemas conhecidos, arquivos afetados e prioridade. Ele deve ser revisado a cada sprint para evitar que o assistente cresça sem organização arquitetural.

## Escopo da Análise

A análise cobre os módulos atuais do ZYRON:

- `main.py`
- `core/`
- `ai/`
- `voice/`
- `commands/`
- `automation/`
- `services/`
- `database/`
- `tests/`

Também considera integrações futuras solicitadas para Spotify API, Google Calendar API, Gmail API, SQLite, PostgreSQL, ChromaDB, memória vetorial, plugins, dashboard web, painel administrativo, multiusuário, reconhecimento facial, IoT, Docker, Kubernetes e AWS.

## Débitos Técnicos Atuais

| Item | Problema conhecido | Arquivos afetados | Prioridade |
| --- | --- | --- | --- |
| Captura de microfone ausente | `listen_once()` é placeholder e não captura áudio real. | `voice/speech_to_text.py` | Alta |
| Playback de TTS ausente | O áudio é gerado em MP3, mas não é reproduzido automaticamente. | `voice/text_to_speech.py` | Alta |
| Wake word textual | A wake word é detectada após transcrição por string matching, não por áudio. | `voice/wake_word.py` | Alta |
| Loop sem isolamento de falhas | Exceções de STT, TTS, banco, clima ou Ollama podem encerrar a aplicação. | `core/application.py`, `commands/command_router.py` | Alta |
| Automação por shell | `shell=True` é frágil e exige allowlist antes de uso real com fala do usuário. | `automation/app_launcher.py` | Alta |
| Interpretação rígida | Regras por prefixo não entendem linguagem natural flexível. | `commands/command_interpreter.py` | Média |
| Roteador concentrado | `CommandRouter` crescerá demais com Spotify, Calendar, Gmail, IoT e financeiro. | `commands/command_router.py` | Média |
| HTTP sem retry/backoff | Ollama e OpenWeather têm timeout, mas não política de retries. | `ai/ollama_client.py`, `services/weather_service.py` | Média |
| SQLite sem migrações | O schema é inline e não versionado. | `database/sqlite_repository.py` | Média |
| Memória limitada | Persistência atual salva apenas histórico bruto de interações. | `database/sqlite_repository.py` | Alta |
| Configuração monolítica | Secrets e preferências convivem no mesmo `Settings`. | `core/config.py` | Média |
| Poucos testes | Há apenas cobertura básica para uma intenção de pesquisa. | `tests/test_command_interpreter.py` | Alta |
| Ausência de logs | Não há logging estruturado, auditoria ou rastreabilidade. | Projeto inteiro | Média |

## Melhorias Pendentes

| Melhoria | Descrição | Arquivos afetados | Prioridade |
| --- | --- | --- | --- |
| Microfone real | Integrar WASAPI, `sounddevice` ou backend equivalente para Windows. | `voice/speech_to_text.py` | Alta |
| Reprodução real | Tocar o MP3/WAV gerado pelo TTS com player local confiável. | `voice/text_to_speech.py` | Alta |
| Wake word acústica | Usar openWakeWord, Porcupine ou modelo local dedicado. | `voice/wake_word.py` | Alta |
| Permissões por risco | Classificar comandos em baixo, médio, alto e crítico. | `core/models.py`, `commands/`, `automation/` | Alta |
| Catálogo de apps | Mapear VSCode, Spotify, Chrome, Steam, Discord e apps customizados. | `automation/app_launcher.py`, `database/` | Alta |
| Cache de clima | Salvar resposta OpenWeather por janela de tempo. | `services/weather_service.py`, `database/` | Média |
| Intents por IA | Pedir ao Ollama para classificar comandos em JSON validado. | `commands/command_interpreter.py`, `ai/ollama_client.py` | Média |
| Handlers por domínio | Separar handlers de música, agenda, e-mail, clima, apps e financeiro. | `commands/` | Média |
| Memória persistente | Separar histórico, preferências, fatos e memórias episódicas. | `database/`, futuro `memory/` | Alta |
| Banco vetorial | Adicionar ChromaDB, SQLite-VSS ou PostgreSQL/pgvector para busca semântica. | futuro `memory/`, `ai/`, `database/` | Média |
| Dashboard Web | Exibir status, logs, histórico, configuração e saúde das integrações. | futuro `dashboard/` | Baixa |
| Painel administrativo | Gerenciar usuários, permissões, plugins, tokens e aliases. | futuro `admin/` | Baixa |
| Docker | Padronizar ambiente de desenvolvimento e serviços auxiliares. | futuro `Dockerfile`, `docker-compose.yml` | Baixa |
| Kubernetes/AWS | Planejar apenas para cenário remoto, multiusuário ou corporativo. | infraestrutura futura | Baixa |
| Reconhecimento facial | Identificar usuário antes de ações sensíveis. | futuro `vision/` | Baixa |
| IoT | Controlar dispositivos via Home Assistant/MQTT. | futuro `iot/` | Baixa |

## Refatorações Futuras

| Refatoração | Objetivo | Arquivos afetados | Prioridade |
| --- | --- | --- | --- |
| Criar interfaces/protocols | Permitir troca de STT, TTS, IA, banco e automação sem alterar núcleo. | `core/`, `ai/`, `voice/`, `automation/`, `services/` | Média |
| Separar command handlers | Evitar crescimento excessivo do roteador. | `commands/command_router.py` | Alta |
| Criar camada de lifecycle | Controlar startup, shutdown, health checks, workers e filas. | `core/application.py`, `main.py` | Média |
| Criar repositórios especializados | Separar interações, memórias, aliases, tokens, agenda, e-mail e finanças. | `database/sqlite_repository.py` | Alta |
| Adotar migrações | Versionar evolução do schema sem perda de dados. | `database/` | Média |
| Injetar clientes HTTP | Facilitar mocks, retries, circuit breaker e observabilidade. | `ai/ollama_client.py`, `services/weather_service.py` | Média |
| Normalizar configuração | Separar secrets, preferências, paths e flags de runtime. | `core/config.py` | Média |
| Criar plugin manager | Permitir novas integrações sem modificar o núcleo. | futuro `plugins/`, `commands/`, `services/` | Média |
| Adicionar lint/type check | Padronizar estilo e reduzir regressões. | Projeto inteiro | Média |

## Problemas Conhecidos

- O assistente ainda não recebe áudio real porque a captura de microfone é placeholder.
- O assistente ainda não fala no alto-falante porque o TTS apenas salva MP3 temporário.
- A wake word não é acústica e depende de texto transcrito.
- A saudação inicial usa clima, mas retorna fallback quando não existe `OPENWEATHER_API_KEY`.
- Falhas de rede em Ollama/OpenWeather não têm retry/backoff centralizado.
- Automação por shell precisa de allowlist antes de receber comandos livres por voz.
- O banco não possui migrações nem tabelas futuras para memórias, aliases, tokens ou finanças.
- Não há sistema de permissões para Gmail, Calendar, IoT, finanças ou shell.
- Integrações Spotify API, Google Calendar API e Gmail API ainda não possuem módulos próprios.
- Não há dashboard web, painel administrativo, multiusuário, Docker, Kubernetes ou AWS configurados.

## Priorização Recomendada

### Alta

1. Captura real de microfone.
2. Playback real de TTS.
3. Wake word acústica.
4. Tratamento de exceções no loop principal.
5. Catálogo seguro de aplicativos.
6. Sistema de permissões por risco.
7. Ampliação de testes unitários.
8. Persistência separada para memórias e aliases.

### Média

1. Classificação de intents via Ollama.
2. Cache e retries para integrações HTTP.
3. Migrações SQLite.
4. Interfaces/protocols para módulos centrais.
5. Logging estruturado e auditoria.
6. Banco vetorial local.
7. Sistema de plugins.
8. Handlers por domínio.

### Baixa

1. Dashboard web.
2. Painel administrativo.
3. Docker para desenvolvimento.
4. Kubernetes/AWS para implantação avançada.
5. Reconhecimento facial.
6. Controle de dispositivos IoT.

## Critérios de Conclusão

Um débito técnico só deve ser considerado resolvido quando:

- A implementação estiver versionada.
- Houver testes automatizados quando aplicável.
- A documentação pública ou interna estiver atualizada.
- O risco de segurança tiver sido reavaliado.
- O comportamento estiver integrado ao fluxo principal ou isolado por feature flag.
- Logs e mensagens de erro forem suficientes para diagnosticar falhas.
