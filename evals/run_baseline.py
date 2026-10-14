"""Reexecuta a versao legada para obter latencia/tokens comparaveis.

Requer HF_TOKEN e disponibilidade do modelo legado no Hugging Face.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.evaluator import avaliar_resposta  # noqa: E402
from scripts.token_utils import contar_tokens  # noqa: E402
from src.chatbot import adicionar_mensagem, carregar_credenciais, criar_cliente, inicializar_historico  # noqa: E402


def main() -> None:
    token = carregar_credenciais()
    if not token:
        raise SystemExit("HF_TOKEN nao encontrado. Configure .env antes de executar o baseline.")

    cliente = criar_cliente(token)
    casos = json.loads((ROOT / "evals" / "eval_set.json").read_text(encoding="utf-8"))
    resultados = []

    for caso in casos:
        historico = inicializar_historico()

        # Prelude apenas para o caso de memoria.
        for pre in caso.get("prelude", []):
            msgs = historico + [{"role": "user", "content": pre}]
            resp = cliente.chat_completion(messages=msgs, max_tokens=512, temperature=0.3)
            texto_pre = resp.choices[0].message.content
            historico = adicionar_mensagem(historico, "user", pre)
            historico = adicionar_mensagem(historico, "assistant", texto_pre)

        msgs = historico + [{"role": "user", "content": caso["pergunta"]}]
        inicio = time.perf_counter()
        resp = cliente.chat_completion(messages=msgs, max_tokens=512, temperature=0.3)
        latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
        texto = resp.choices[0].message.content
        avaliacao = avaliar_resposta(caso["id"], texto)

        resultados.append(
            {
                "id": caso["id"],
                "pergunta": caso["pergunta"],
                "resposta": texto,
                "latencia_ms": latencia_ms,
                "tokens_turno_aprox": contar_tokens(caso["pergunta"] + "\n" + texto),
                "structured_output_valido": False,
                **avaliacao,
            }
        )
        print(f"Baseline {caso['id']}: {avaliacao['avaliacao']}")

    resumo = {
        "total": len(resultados),
        "adequadas": sum(r["avaliacao"] == "adequada" for r in resultados),
        "parcialmente_adequadas": sum(r["avaliacao"] == "parcialmente_adequada" for r in resultados),
        "inadequadas": sum(r["avaliacao"] == "inadequada" for r in resultados),
        "latencia_media_ms": round(statistics.mean(r["latencia_ms"] for r in resultados), 2),
        "tokens_medios_turno_aprox": round(statistics.mean(r["tokens_turno_aprox"] for r in resultados), 2),
        "structured_output_accuracy_percent": None,
    }
    resumo["nota_eval_percentual"] = round(100 * resumo["adequadas"] / len(resultados), 2)

    destino = ROOT / "evals" / "baseline_results.json"
    destino.write_text(
        json.dumps({"resumo": resumo, "resultados": resultados}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nSalvo em: {destino}")


if __name__ == "__main__":
    main()
