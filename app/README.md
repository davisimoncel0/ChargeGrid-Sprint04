# Interface ChargeGrid

Na raiz do projeto, configure o Ollama e instale `pip install -r requirements.txt`. Baixe os modelos `ollama pull nomic-embed-text`, `ollama pull qwen3:8b` e `ollama pull llama3.2:3b` (ou ajuste os nomes para modelos disponiveis). Rode `python scripts/index_rag.py` e depois `python app/main.py`. Abra o endereco local informado pelo Gradio. Para acesso publico, configure deploy de forma segura; a URL publica nao e criada automaticamente.
