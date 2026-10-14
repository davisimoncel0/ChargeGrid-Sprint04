# Relatorio de Modelos - Sprint 03

Comparacao executada sobre o mesmo eval set e com o mesmo pipeline da Sprint 03.

| Modelo | Adequadas | Nota eval | Structured output | Latencia media | Tokens/turno |
|---|---:|---:|---:|---:|---:|
| qwen3:8b | 8/8 | 100.0% | 100.0% | 18638.79 ms | 125.5 |
| llama3.2:3b | 2/8 | 25.0% | 25.0% | 3625.18 ms | 164.5 |

## Criterio de escolha

O modelo principal deve equilibrar aderencia ao schema, qualidade no eval e latencia. No resultado final do grupo, gpt-oss:120b-cloud e qwen3:8b atingiram 100% de structured output; o GPT-OSS foi adotado como principal por atender diretamente ao modelo solicitado e apresentar menor latencia no eval.
