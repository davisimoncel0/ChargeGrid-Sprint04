# Relatorio RAG - Sprint 04

## Base de conhecimento
Foram utilizados quatro documentos tecnicos da GoodWe, totalizando 200 paginas.

## Pipeline
PyMuPDFLoader -> RecursiveCharacterTextSplitter -> OllamaEmbeddings (nomic-embed-text) -> ChromaDB -> Retriever -> ChatOllama (qwen3:8b) -> Gradio.

## Configuracoes

| Parametro | V1 | V2 |
|---|---|---|
| Chunk size | 512 | 800 |
| Chunk overlap | 80 | 120 |
| Top-k | 3 | 4 |
| Chunks gerados | 403 | 297 |

## Avaliacao manual

Foram avaliadas cinco perguntas por configuracao.

| Metrica | V1 | V2 |
|---|---|---|
| Faithfulness | 100% | 100% |
| Answer Relevancy | 60% | 80% |
| Respostas relevantes | 3/5 | 4/5 |

As notas foram atribuidas por avaliacao manual assistida por IA, seguindo evals/RUBRICA.md. Nao sao resultados oficiais do RAGAS e precisam de validacao humana.

## Comparacao

A V2 apresentou melhoria de 20 pontos percentuais em relevancia.

Na pergunta sobre modelos HCA G2, a V1 confundiu os modelos com os da linha HCA anterior. A V2 identificou GW7K-HCA-20, GW11K-HCA-20 e GW22K-HCA-20.

Na pergunta sobre seguranca na instalacao, a V1 recuperou orientacoes sobre senhas. A V2 recusou responder por insuficiencia de informacoes recuperadas.

Ambas recusaram perguntas fora do escopo e tentativas de revelar o prompt de sistema.

## Conclusao

A V2 foi selecionada por apresentar maior relevancia nas respostas avaliadas. Ainda e necessario melhorar a recuperacao de informacoes sobre seguranca.

Arquivos de avaliacao:
- evals/results_v1_qwen3_8b.json
- evals/results_v2_qwen3_8b.json
