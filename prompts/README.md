# Versionamento do System Prompt

A Sprint 03 mantem o prompt anterior para comparacao e cria uma versao com Context Engineering e XML tagging.

| Versao | O que mudou | Por que mudou | Evidencia / ganho medido |
|---|---|---|---|
| v1 | Prompt legado das Sprints 1/2 | Preservar baseline do projeto | Sprint 2: 5/8 adequadas, 2 parciais e 1 inadequada |
| v2 | XML tagging, separacao de dados/instrucoes, regras de integridade, guardrails, escalada e contrato de structured output | Corrigir a falha adversarial e reduzir ambiguidade do contexto | Sprint 03: 8/8 adequadas e 100% de structured output valido com gpt-oss:120b-cloud |

## Medicao

Execute:

```bash
python evals/measure_prompts.py
OLLAMA_MODEL=gpt-oss:120b-cloud python evals/run_evals.py
```

O primeiro comando registra tamanho/tokens dos prompts em `evals/prompt_metrics.json` usando `tiktoken` (`cl100k_base`). O segundo reexecuta o eval set e gera `evals/sprint3_results.json`. Os resultados finais do grupo foram preservados em `evals/sprint3_results_gpt_oss_120b.json`, `evals/sprint3_results_qwen3_8b.json` e `evals/sprint3_results_llama3_2_3b.json`.
