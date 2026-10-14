# ChargeGrid — Sprint 04

Evolução do chatbot da Sprint 03 com RAG sobre manuais técnicos da GoodWe. O projeto utiliza embeddings locais (`nomic-embed-text`), ChromaDB persistente, Ollama e interface Gradio. Os módulos anteriores permanecem em `src/chain`, `src/guardrails` e `src/schemas`.

## Como executar

1. Utilizar Python 3.11, criar um ambiente virtual e instalar as dependências com `pip install -r requirements.txt`.
2. Instalar e iniciar o Ollama. Baixar os modelos com `ollama pull nomic-embed-text`, `ollama pull qwen3:8b` e `ollama pull llama3.2:3b`.
3. Criar o arquivo `.env` com base em `.env.example`.
4. Indexar os documentos da pasta `data/knowledge_base`:
   - V1: `python scripts/index_rag.py --size 512 --overlap 80 --collection chargegrid_v1`
   - V2/V3: `python scripts/index_rag.py --size 800 --overlap 120 --collection chargegrid_v2`
5. Iniciar a interface com `python app/main.py`.

A V3 utiliza o prompt `prompts/rag_v3.md` e uma busca direcionada ao manual HCA G2 para perguntas sobre instalação e segurança. Ela reutiliza a coleção `chargegrid_v2`. A existência da V3 no projeto não significa que a interface a selecione automaticamente; para testá-la diretamente, utilize a função `answer` com `version="v3"` e `collection="chargegrid_v2"`.

## Testes e resultados

Os testes foram executados localmente com Ollama e registrados na pasta `evals/`.

- `evals/results_v1_qwen3_8b.json`: resultados da V1.
- `evals/results_v2_qwen3_8b.json`: resultados da V2.
- `evals/results_v3_qwen3_8b.json`: resultados da V3.
- `evals/rag_model_comparison.json`: comparação do RAG V2 com Qwen3 8B e Llama 3.2 3B, em cinco perguntas por modelo.

Na bateria de cinco perguntas, a avaliação funcional preliminar registrou 3/5 respostas relevantes na V1, 4/5 na V2 e 5/5 na V3. Os resultados não são métricas oficiais do RAGAS e não comprovam fidelidade documental integral. Uma citação da V3 sobre qualificação profissional ainda requer validação.

Os detalhes de configuração, limitações e análise estão em `docs/relatorio_rag.md` e no relatório `docs/Relatorio_Sprint04_IA.pdf`.

## Observações

O arquivo `.env` não deve ser enviado ao repositório. Antes de redistribuir os manuais técnicos, é necessário verificar as respectivas permissões de uso.
