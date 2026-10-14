"""Mede o custo de contexto dos prompts v1 e v2 usando tiktoken."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    try:
        import tiktoken
    except ImportError as exc:
        raise SystemExit("tiktoken nao instalado. Rode: pip install -r requirements.txt") from exc

    enc = tiktoken.get_encoding("cl100k_base")
    arquivos = [
        ROOT / "prompts" / "system_prompt_v1.md",
        ROOT / "prompts" / "system_prompt_v2.md",
    ]
    resultados = {"metodo": "tiktoken/cl100k_base", "prompts": {}}
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8")
        resultados["prompts"][arquivo.name] = {
            "caracteres": len(texto),
            "palavras": len(texto.split()),
            "tokens": len(enc.encode(texto)),
        }

    destino = ROOT / "evals" / "prompt_metrics.json"
    destino.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    print(f"\nSalvo em: {destino}")


if __name__ == "__main__":
    main()
