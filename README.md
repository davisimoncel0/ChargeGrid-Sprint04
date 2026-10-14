# Chatbot GoodWe - ChargeGrid Intelligence - Sprint 03

Projeto do **EV Challenge 2026 - FIAP x GoodWe**, disciplina **Prompt and Artificial Intelligence**. A Sprint 03 evolui o mesmo chatbot das Sprints 1/2, preservando a versao legada e refatorando o nucleo conversacional com LangChain LCEL, memoria por sessao, structured output Pydantic v2, Context Engineering e guardrails.

## Integrantes

- Davi Simoncelo - RM 571738 - 1CCPK
- Augusto de Souza Avila - RM 570839 - 1CCPK
- Joao Pedro Sousa - RM 573962 - 1CCPK
- Matheus Evangelista Silva - RM 568593 - 1CCPK
- Murilo Lima de Carvalho - RM 570156 - 1CCPK

## Evolucao da arquitetura

**Sprints 1/2 (legado):** `src/chatbot.py` usa Hugging Face Inference API, Qwen 2.5 e lista de historico gerenciada manualmente.

**Sprint 03:**

```text
ChatPromptTemplate
      |
ChatOllama
      |
PydanticOutputParser (ConsultaRecarga)
```

A chain e envolvida por `RunnableWithMessageHistory`, com historicos separados por `session_id`. A memoria usa `ConversationTokenBufferMemory` com limite de tokens. Antes da chamada ao modelo existem validacoes deterministicas de escopo e seguranca.

## Estrutura

```text
prompts/                 system prompts versionados e tabela de evolucao
src/chain/               LCEL + memoria por sessao
src/schemas/             Pydantic v2 + field_validator
src/guardrails/          scope validator + moderation + output validator
evals/                   eval set e resultados medidos
docs/                    relatorio final e comparacao de modelos
scripts/                 utilitarios e bonus opcional
```

## Requisitos

- Python 3.12 recomendado para a stack usada no projeto
- Ollama instalado e em execucao
- Modelo principal testado: `gpt-oss:120b-cloud` (GPT-OSS 120B via Ollama Cloud)
- Segundo modelo comparado: `qwen3:8b` (Ollama local)
- Modelo adicional avaliado: `llama3.2:3b`

> O modelo exigido na arquitetura de referencia (`gpt-oss:120b`) foi executado na variante `gpt-oss:120b-cloud`, disponibilizada pelo Ollama Cloud. A chain continua usando `ChatOllama`; a diferenca e apenas onde o modelo e processado.

## Instalacao

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Configuracao padrao:

```env
OLLAMA_MODEL=gpt-oss:120b-cloud
OLLAMA_BASE_URL=http://localhost:11434
TEMPERATURE=0.2
TOP_P=0.9
MAX_TOKENS=512
MAX_MEMORY_TOKENS=1200
```

> Nunca commite `.env` ou API keys. O arquivo real esta no `.gitignore`; somente `.env.example` faz parte do repositorio.

## Executar o chatbot

Em um terminal, mantenha o Ollama ativo:

```bash
ollama serve
```

Em outro terminal:

```bash
source .venv/bin/activate
python -m src.main
```

Teste de memoria sugerido em 3 turnos:

1. `Estou com erro OCPP no carregador.`
2. `Ja reiniciei ele.`
3. `Qual e o proximo passo?`

## Guardrails e schema

```bash
python scripts/smoke_tests.py
```

## Context Engineering / tokens

```bash
python evals/measure_prompts.py
```

O comando usa `tiktoken` com a codificacao `cl100k_base` e gera `evals/prompt_metrics.json`, registrando caracteres, palavras e tokens dos prompts v1 e v2.

## Eval principal da Sprint 03

```bash
OLLAMA_MODEL=gpt-oss:120b-cloud python evals/run_evals.py
```

Resultado final do modelo principal, preservado em `evals/sprint3_results_gpt_oss_120b.json`:

- 8/8 respostas adequadas
- 100% de nota no eval
- 100% de structured output valido
- 1433.01 ms de latencia media
- 166 tokens medios/turno (aproximacao do runner)

## Comparacao de modelos

Os resultados medidos estao em:

- `evals/sprint3_results_gpt_oss_120b.json`
- `evals/sprint3_results_qwen3_8b.json`
- `evals/sprint3_results_llama3_2_3b.json`
- `docs/relatorio_modelos.md`

Resumo:

| Modelo | Eval | Structured output | Latencia media | Tokens/turno |
|---|---:|---:|---:|---:|
| gpt-oss:120b-cloud | 100% | 100% | 1433.01 ms | 166 |
| qwen3:8b | 100% | 100% | 22641.46 ms | 119 |
| llama3.2:3b | 25% | 25% | 2663.39 ms | 114.62 |

## Baseline das Sprints 1/2

A versao legada foi preservada em `src/chatbot.py` e os resultados historicos estao em `tests/resultados.md`: 5/8 adequadas, 2 parcialmente adequadas e 1 inadequada.

Latencia e tokens nao foram registrados na execucao historica. A reexecucao do legado depende da credencial externa da Hugging Face (`HF_TOKEN`), portanto esses valores nao foram inventados no relatorio.

## Relatorio final

- `docs/Relatorio_Sprint03_IA.pdf`
- `docs/Relatorio_Sprint03_IA.docx`
- `docs/relatorio_modelos.md`

## Bonus (+1)

`scripts/bonus_multi_provider.py` demonstra dois provedores e dois prompts. Esse item e opcional e exige credencial Hugging Face para o segundo provedor.

## Versao legada preservada

`src/chatbot.py`, `tests/modelo-de-teste.md` e `tests/resultados.md` foram mantidos para comprovar o comparativo antes/depois.

### Validação de saída
Além dos guardrails de entrada e do schema Pydantic, a Sprint 03 possui uma validação determinística de saída em `src/guardrails/output_validator.py`. Ela bloqueia valores técnicos específicos não sustentados pelo contexto, como portas numéricas, códigos de erro, URLs de suporte ou valores de latência/jitter inventados. O `evals/evaluator.py` também verifica esse critério de integridade.
