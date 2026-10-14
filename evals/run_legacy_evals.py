"""Eval da versao legada/manual das Sprints 1 e 2."""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from evals.evaluator import avaliar_resposta
from scripts.token_utils import contar_tokens
from src.chatbot import (
    adicionar_mensagem,
    carregar_credenciais,
    conversar,
    criar_cliente,
    inicializar_historico,
)


def executar() -> dict:
    # Carrega o mesmo conjunto de testes usado na Sprint 03
    casos = json.loads(
        (ROOT / "evals" / "eval_set.json").read_text(
            encoding="utf-8"
        )
    )

    # Token HF da versao antiga
    hf_token = carregar_credenciais()

    if not hf_token:
        raise RuntimeError(
            "HF_TOKEN nao encontrado no arquivo .env."
        )

    cliente = criar_cliente(hf_token)

    resultados = []

    for caso in casos:
        # Cada teste inicia uma conversa nova
        historico = inicializar_historico()

        # ---------------------------------------
        # Prelude para casos que precisam memoria
        # ---------------------------------------

        prelude_falhou = False

        for mensagem_previa in caso.get("prelude", []):
            try:
                _, historico = conversar(
                    cliente,
                    historico,
                    mensagem_previa,
                )

            except Exception as erro:
                print(
                    f"Teste {caso['id']} - erro no prelude: "
                    f"{type(erro).__name__}: {erro}"
                )

                prelude_falhou = True
                break

        inicio = time.perf_counter()

        try:
            if prelude_falhou:
                raise RuntimeError(
                    "Falha durante as mensagens anteriores "
                    "do teste de memoria."
                )

            resposta, historico = conversar(
                cliente,
                historico,
                caso["pergunta"],
            )

            latencia_ms = round(
                (time.perf_counter() - inicio) * 1000,
                2,
            )

            avaliacao = avaliar_resposta(
                caso["id"],
                resposta,
            )

            tokens_pergunta = contar_tokens(
                caso["pergunta"]
            )

            tokens_resposta = contar_tokens(
                resposta
            )

            # Aproximacao do turno atual.
            tokens_turno = contar_tokens(
                caso["pergunta"]
                + "\n"
                + resposta
            )

            resultado = {
                "id": caso["id"],
                "categoria_teste": caso["categoria"],
                "pergunta": caso["pergunta"],
                "resposta": resposta,

                # Versao antiga nao tinha Pydantic
                "structured_output_valido": None,

                "tokens_pergunta": tokens_pergunta,
                "tokens_resposta": tokens_resposta,
                "tokens_turno_aprox": tokens_turno,

                "latencia_ms": latencia_ms,

                **avaliacao,
            }

            resultados.append(resultado)

            print(
                f"Teste {caso['id']}: "
                f"{avaliacao['avaliacao']} "
                f"({latencia_ms} ms)"
            )

        except Exception as erro:
            latencia_ms = round(
                (time.perf_counter() - inicio) * 1000,
                2,
            )

            resultados.append(
                {
                    "id": caso["id"],
                    "categoria_teste": caso["categoria"],
                    "pergunta": caso["pergunta"],
                    "resposta": None,

                    "structured_output_valido": None,

                    "tokens_pergunta": contar_tokens(
                        caso["pergunta"]
                    ),
                    "tokens_resposta": 0,
                    "tokens_turno_aprox": contar_tokens(
                        caso["pergunta"]
                    ),

                    "latencia_ms": latencia_ms,

                    "avaliacao": "inadequada",

                    "erro_execucao": (
                        f"{type(erro).__name__}: {erro}"
                    ),

                    "checks": {
                        "execucao": False
                    },

                    "criterios_aprovados": 0,
                    "criterios_totais": 1,
                    "taxa": 0.0,
                }
            )

            print(
                f"Teste {caso['id']}: inadequada "
                f"- erro de execucao "
                f"({latencia_ms} ms)"
            )

    # ---------------------------------------
    # Resumo da reexecucao
    # ---------------------------------------

    adequadas = sum(
        r["avaliacao"] == "adequada"
        for r in resultados
    )

    parciais = sum(
        r["avaliacao"] == "parcialmente_adequada"
        for r in resultados
    )

    inadequadas = sum(
        r["avaliacao"] == "inadequada"
        for r in resultados
    )

    latencias = [
        r["latencia_ms"]
        for r in resultados
    ]

    tokens_turno = [
        r["tokens_turno_aprox"]
        for r in resultados
    ]

    resumo = {
        "total": len(resultados),

        "adequadas_reexecucao": adequadas,
        "parcialmente_adequadas_reexecucao": parciais,
        "inadequadas_reexecucao": inadequadas,

        "nota_eval_reexecucao_percentual": round(
            100 * adequadas / len(resultados),
            2,
        ),

        "latencia_media_ms": round(
            statistics.mean(latencias),
            2,
        ),

        "tokens_medios_turno_aprox": round(
            statistics.mean(tokens_turno),
            2,
        ),

        # Na versao antiga nao havia parser/schema Pydantic
        "structured_output_accuracy_percent": None,

        # Resultado historico documentado na Sprint 2
        "resultado_historico_sprint2": {
            "adequadas": 5,
            "parcialmente_adequadas": 2,
            "inadequadas": 1,
            "adequacao_total_percentual": 62.5,
        },
    }

    return {
        "observacao": (
            "A qualidade historica oficial da Sprint 2 vem de "
            "tests/resultados.md. Esta reexecucao serve principalmente "
            "para medir latencia e tokens da arquitetura manual, pois o "
            "endpoint/modelo remoto e o system prompt podem ter mudado "
            "desde junho de 2026."
        ),
        "resumo": resumo,
        "resultados": resultados,
    }


def main() -> None:
    dados = executar()

    destino = (
        ROOT
        / "evals"
        / "legacy_results.json"
    )

    destino.write_text(
        json.dumps(
            dados,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nResumo:")
    print(
        json.dumps(
            dados["resumo"],
            indent=2,
            ensure_ascii=False,
        )
    )

    print(f"\nSalvo em: {destino}")


if __name__ == "__main__":
    main()