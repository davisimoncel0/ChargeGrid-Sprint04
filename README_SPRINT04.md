# ChargeGrid — Sprint 04

Evolucao da Sprint 03: RAG sobre manuais GoodWe, ChromaDB persistente, citacoes e interface Gradio. Codigo original preservado em `src/chain`, `src/guardrails`, `src/schemas`.

## Como rodar
1. Python 3.11; criar venv e instalar `pip install -r requirements.txt`.
2. Instalar/iniciar Ollama; baixar `nomic-embed-text`, `qwen3:8b` e `llama3.2:3b`.
3. Configurar `.env` conforme `.env.example` (modelo e host). Sem API keys no Git.
4. `python scripts/index_rag.py --size 512 --overlap 80 --collection chargegrid_v1`
5. `python scripts/index_rag.py --size 800 --overlap 120 --collection chargegrid_v2`
6. `python app/main.py` (a interface consulta a colecao v2).
7. Rodar os testes de `docs/relatorio_rag.md`, preencher notas manuais em `evals/` e atualizar o PDF final.

**Importante:** nao foi possivel executar Ollama nem obter scores reais aqui. O PDF e uma versao preliminar, nao comprovacao de ganho. Confirmar licenca de redistribuicao dos PDFs antes de tornar o repositorio publico.
