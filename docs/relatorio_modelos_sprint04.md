# Comparacao de Modelos - Sprint 04

## Modelos avaliados

Os modelos qwen3:8b e llama3.2:3b foram avaliados com o mesmo conjunto de oito testes.

| Metrica | Qwen3 8B | Llama 3.2 3B |
|---|---|---|
| Testes adequados | 8/8 | 2/8 |
| Taxa de sucesso | 100% | 25% |
| Structured output | 100% | 25% |
| Latencia media | 18638.79 ms | 3625.18 ms |
| Tokens por turno | 125.5 | 164.5 |

## Analise

O Qwen3 8B apresentou maior adequacao das respostas e melhor conformidade com o formato estruturado.

O Llama 3.2 3B apresentou menor latencia, mas falhou em seis dos oito testes.

## Modelo selecionado

O Qwen3 8B foi escolhido como modelo principal da Sprint 04 por apresentar maior confiabilidade nos testes realizados.

Os resultados desta comparacao foram obtidos com o pipeline de avaliacao da Sprint 03. A avaliacao RAG da Sprint 04 foi realizada separadamente.
