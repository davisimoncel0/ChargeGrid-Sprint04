"""Interface de terminal da Sprint 03 preservando a identidade das Sprints 1 e 2."""

import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Permite executar com python -m src.main ou python src/main.py
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from src.chain.builder import ChatbotGoodWe


def modelo_atual():
    load_dotenv(ROOT / ".env")
    return os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


def main():
    session_id = "terminal"

    print("=" * 60)
    print("  Chatbot GoodWe — ChargeGrid Intelligence")
    print(f"  Modelo: {modelo_atual()} via Ollama + LangChain LCEL")
    print("  EV Challenge 2026 · FIAP × GoodWe")
    print("=" * 60)
    print()

    try:
        chatbot = ChatbotGoodWe(model=modelo_atual())
    except Exception as erro:
        print(f"[ERRO] Nao foi possivel iniciar o chatbot: {erro}")
        print("Confira se o Ollama esta rodando e se as dependencias foram instaladas.")
        return

    print("Chatbot pronto.")
    print("Digite 'sair' para encerrar ou 'limpar' para apagar a memoria.")
    print()

    while True:
        print("-" * 60)

        try:
            pergunta = input("Voce: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nEncerrando...")
            break

        if not pergunta:
            continue

        if pergunta.lower() in {"sair", "exit", "quit"}:
            print()
            print("Bot: Ate logo!")
            break

        if pergunta.lower() in {"limpar", "reset", "reiniciar"}:
            chatbot.limpar(session_id)
            print()
            print("Bot: Historico da conversa apagado.")
            print()
            continue

        try:
            resposta = chatbot.responder(
                pergunta,
                session_id=session_id
            )

            print()
            print(f"Bot: {resposta.resposta}")
            print()

        except Exception as erro:
            print()
            print(f"[ERRO] {erro}")
            print()


if __name__ == "__main__":
    main()