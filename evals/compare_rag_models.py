import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.pipeline import answer

MODELS = ["qwen3:8b", "llama3.2:3b"]
EVAL_SET = ROOT / "evals" / "rag_eval_set.json"
OUTPUT = ROOT / "evals" / "rag_model_comparison.json"

questions = json.loads(EVAL_SET.read_text(encoding="utf-8"))
results = []

for model in MODELS:
    print(f"\nAvaliando {model}...")

    for item in questions:
        question = item["question"]
        print(f"Pergunta: {question}")

        start = time.perf_counter()

        try:
            response = answer(
                question,
                model=model,
                version="v2",
                k=4,
                collection="chargegrid_v2"
            )

            result = {
                "model": model,
                "question": question,
                "answer": response["answer"],
                "sources": response["sources"],
                "contexts": response["contexts"],
                "latency_seconds": round(time.perf_counter() - start, 2),
                "faithfulness": None,
                "answer_relevancy": None
            }

        except Exception as error:
            result = {
                "model": model,
                "question": question,
                "error": str(error),
                "latency_seconds": round(time.perf_counter() - start, 2)
            }

        results.append(result)

OUTPUT.write_text(
    json.dumps(results, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"\nResultados salvos em {OUTPUT}")
