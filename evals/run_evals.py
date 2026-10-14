"""Reexecuta o eval set sobre a Sprint 03 e salva metricas reais."""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from langchain_core.exceptions import OutputParserException


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from evals.evaluator import avaliar_resposta
from scripts.token_utils import contar_tokens
from src.chain.builder import ChatbotGoodWe


def executar() -> dict:
    casos = json.loads(
        (ROOT / "evals" / "eval_set.json").read_text(
            encoding="utf-8"
        )
    )

    bot = ChatbotGoodWe()

    resultados = []

    for caso in casos:
        session_id = f"eval-{caso['id']}"

        bot.limpar(session_id)

        # ---------------------------------------
        # Mensagens anteriores para teste de memoria
        # ---------------------------------------

        prelude_falhou = False

        for mensagem_previa in caso.get("prelude", []):
            try:
                bot.responder(
                    mensagem_previa,
                    session_id=session_id,
                )

            except Exception as erro:
                print(
                    f"Teste {caso['id']} - erro no prelude: "
                    f"{type(erro).__name__}"
                )

                prelude_falhou = True
                break

        # ---------------------------------------
        # Executar pergunta principal
        # ---------------------------------------

        inicio = time.perf_counter()

        try:
            if prelude_falhou:
                raise RuntimeError(
                    "Falha nas mensagens anteriores do teste."
                )

            saida = bot.responder(
                caso["pergunta"],
                session_id=session_id,
            )

            latencia_ms = round(
                (time.perf_counter() - inicio) * 1000,
                2,
            )

            texto = saida.resposta

            avaliacao = avaliar_resposta(
                caso["id"],
                texto,
            )

            resultado = {
                "id": caso["id"],
                "categoria_teste": caso["categoria"],
                "pergunta": caso["pergunta"],

                "saida": saida.model_dump(),

                "structured_output_valido": True,

                "erro_parser": None,

                "tokens_pergunta": contar_tokens(
                    caso["pergunta"]
                ),

                "tokens_resposta": contar_tokens(
                    texto
                ),

                "tokens_turno_aprox": contar_tokens(
                    caso["pergunta"]
                    + "\n"
                    + texto
                ),

                "latencia_ms": latencia_ms,

                **avaliacao,
            }

            resultados.append(resultado)

            print(
                f"Teste {caso['id']}: "
                f"{avaliacao['avaliacao']} "
                f"({latencia_ms} ms)"
            )

        # ---------------------------------------
        # Falha de structured output
        # ---------------------------------------

        except OutputParserException as erro:
            latencia_ms = round(
                (time.perf_counter() - inicio) * 1000,
                2,
            )

            # Recupera a resposta bruta do modelo,
            # quando disponivel.
            llm_output = getattr(
                erro,
                "llm_output",
                None,
            )

            if llm_output is None:
                llm_output = str(erro)

            resultado = {
                "id": caso["id"],
                "categoria_teste": caso["categoria"],
                "pergunta": caso["pergunta"],

                "saida": None,

                "saida_bruta_modelo": llm_output,

                "structured_output_valido": False,

                "erro_parser": (
                    "O modelo nao retornou JSON valido "
                    "para o schema Pydantic."
                ),

                "tokens_pergunta": contar_tokens(
                    caso["pergunta"]
                ),

                "tokens_resposta": contar_tokens(
                    llm_output
                ),

                "tokens_turno_aprox": contar_tokens(
                    caso["pergunta"]
                    + "\n"
                    + llm_output
                ),

                "latencia_ms": latencia_ms,

                "avaliacao": "inadequada",

                "checks": {
                    "structured_output": False,
                },

                "criterios_aprovados": 0,
                "criterios_totais": 1,
                "taxa": 0.0,
            }

            resultados.append(resultado)

            print(
                f"Teste {caso['id']}: inadequada "
                f"- structured output invalido "
                f"({latencia_ms} ms)"
            )

        # ---------------------------------------
        # Outros erros
        # ---------------------------------------

        except Exception as erro:
            latencia_ms = round(
                (time.perf_counter() - inicio) * 1000,
                2,
            )

            resultado = {
                "id": caso["id"],
                "categoria_teste": caso["categoria"],
                "pergunta": caso["pergunta"],

                "saida": None,

                "structured_output_valido": False,

                "erro_parser": None,

                "erro_execucao": (
                    f"{type(erro).__name__}: {erro}"
                ),

                "tokens_pergunta": contar_tokens(
                    caso["pergunta"]
                ),

                "tokens_resposta": 0,

                "tokens_turno_aprox": contar_tokens(
                    caso["pergunta"]
                ),

                "latencia_ms": latencia_ms,

                "avaliacao": "inadequada",

                "checks": {
                    "execucao": False,
                },

                "criterios_aprovados": 0,
                "criterios_totais": 1,
                "taxa": 0.0,
            }

            resultados.append(resultado)

            print(
                f"Teste {caso['id']}: inadequada "
                f"- erro de execucao "
                f"({latencia_ms} ms)"
            )

    # ---------------------------------------
    # Resumo
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

    structured_validos = sum(
        1
        for r in resultados
        if r["structured_output_valido"]
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

        "adequadas": adequadas,

        "parcialmente_adequadas": parciais,

        "inadequadas": inadequadas,

        "nota_eval_percentual": round(
            100
            * adequadas
            / len(resultados),
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

        "structured_output_accuracy_percent": round(
            100
            * structured_validos
            / len(resultados),
            2,
        ),
    }

    return {
        "resumo": resumo,
        "resultados": resultados,
    }


def main() -> None:
    dados = executar()

    destino = (
        ROOT
        / "evals"
        / "sprint3_results.json"
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

    print(
        f"\nSalvo em: {destino}"
    )


if __name__ == "__main__":
    main()