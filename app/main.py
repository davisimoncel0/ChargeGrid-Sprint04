import sys
from pathlib import Path
import gradio as gr
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rag.pipeline import answer

def chat(message, history):
    try:
        result = answer(message, version="v2", collection="chargegrid_v2")
        sources = list(dict.fromkeys(f"{s['file']} — página {s['page']}" for s in result['sources']))
        suffix = "\n\n**Fontes recuperadas:**\n" + "\n".join(f"- {s}" for s in sources) if sources else ""
        return result['answer'] + suffix
    except Exception as exc:
        return f"Falha ao consultar a base RAG: {type(exc).__name__}. Verifique Ollama, embeddings e indexação."

if __name__ == "__main__":
    gr.ChatInterface(fn=chat, title="ChargeGrid | Assistente GoodWe", description="Pergunte sobre os documentos técnicos da base. As respostas mostram as fontes recuperadas.", examples=["Quais são as especificações do HCA G2?", "Quais orientações de segurança constam no manual?"], type="messages").launch()
