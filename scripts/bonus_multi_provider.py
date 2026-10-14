"""Bonus opcional: demonstra chamada a dois provedores/modelos e dois prompts.

Provider 1: Ollama via LangChain (Sprint 03)
Provider 2: Hugging Face Inference API (legado)

O script so roda se OLLAMA e HF_TOKEN estiverem configurados. Ele nao e necessario
para os 100 pontos principais.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
from huggingface_hub import InferenceClient  # noqa: E402
from src.chain.builder import ChatbotGoodWe  # noqa: E402


def main() -> None:
    load_dotenv(ROOT / ".env")
    pergunta = "Explique em poucas linhas a diferenca entre OCPP e MODBUS no ChargeGrid."

    ollama = ChatbotGoodWe()
    r1 = ollama.responder(pergunta, session_id="bonus-ollama")
    print("=== Provider 1: Ollama / prompt v2 ===")
    print(r1.resposta)

    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise SystemExit("HF_TOKEN ausente: configure para executar o segundo provider.")

    prompt_v1 = (ROOT / "prompts" / "system_prompt_v1.md").read_text(encoding="utf-8")
    hf = InferenceClient(model="Qwen/Qwen2.5-7B-Instruct", token=token)
    r2 = hf.chat_completion(
        messages=[
            {"role": "system", "content": prompt_v1},
            {"role": "user", "content": pergunta},
        ],
        max_tokens=300,
        temperature=0.2,
    )
    print("\n=== Provider 2: Hugging Face / prompt v1 ===")
    print(r2.choices[0].message.content)


if __name__ == "__main__":
    main()
