"""Compara 2+ modelos usando o mesmo runner de eval da Sprint 03."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.run_evals import executar  # noqa: E402


def avaliar_modelo(model: str) -> dict:
    anterior = os.environ.get("OLLAMA_MODEL")
    os.environ["OLLAMA_MODEL"] = model
    try:
        dados = executar()
    finally:
        if anterior is None:
            os.environ.pop("OLLAMA_MODEL", None)
        else:
            os.environ["OLLAMA_MODEL"] = anterior

    return {
        "model": model,
        **dados["resumo"],
    }


def gerar_markdown(resultados: list[dict]) -> str:
    linhas = [
        "# Relatorio de Modelos - Sprint 03",
        "",
        "Comparacao executada sobre o mesmo eval set e com o mesmo pipeline da Sprint 03.",
        "",
        "| Modelo | Adequadas | Nota eval | Structured output | Latencia media | Tokens/turno |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in resultados:
        linhas.append(
            f"| {r['model']} | {r['adequadas']}/{r['total']} | "
            f"{r['nota_eval_percentual']}% | {r['structured_output_accuracy_percent']}% | "
            f"{r['latencia_media_ms']} ms | {r['tokens_medios_turno_aprox']} |"
        )
    linhas += [
        "",
        "## Criterio de escolha",
        "",
        "O modelo principal deve equilibrar aderencia ao schema, qualidade no eval e latencia. "
        "No resultado final do grupo, gpt-oss:120b-cloud e qwen3:8b atingiram 100% de structured output; o GPT-OSS foi adotado como principal por atender diretamente ao modelo solicitado e apresentar menor latencia no eval.",
    ]
    return "\n".join(linhas) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", default=["gpt-oss:120b-cloud", "qwen3:8b"])
    args = p.parse_args()

    resultados = []
    for model in args.models:
        print(f"Avaliando {model}...")
        resultados.append(avaliar_modelo(model))

    (ROOT / "evals" / "model_comparison_results.json").write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (ROOT / "docs" / "relatorio_modelos.md").write_text(
        gerar_markdown(resultados), encoding="utf-8"
    )
    print("Relatorio atualizado em docs/relatorio_modelos.md")


if __name__ == "__main__":
    main()
