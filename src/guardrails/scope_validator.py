"""Validacao leve de escopo antes da chamada ao LLM."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResultadoEscopo:
    dentro_escopo: bool
    resposta: Optional[str] = None


# Somente casos evidentemente fora de escopo sao bloqueados de forma deterministica.
# Casos ambiguos seguem para o modelo, que tambem possui regras de escopo no prompt.
_PADROES_FORA_ESCOPO = [
    r"corinthians|palmeiras|flamengo|futebol|placar|campeonato",
    r"receita\s+de|como\s+cozinhar|bolo|lasanha",
    r"hor[oó]scopo|signo",
    r"filme\s+em\s+cartaz|serie\s+da\s+netflix",
]


def validar_escopo(texto: str) -> ResultadoEscopo:
    for padrao in _PADROES_FORA_ESCOPO:
        if re.search(padrao, texto, flags=re.IGNORECASE):
            return ResultadoEscopo(
                dentro_escopo=False,
                resposta=(
                    "Esse assunto esta fora do meu escopo. Sou especializado no ChargeGrid "
                    "Intelligence e posso ajudar com eletropostos, tarifas, OCPP, MODBUS, "
                    "sessoes de recarga, consumo e smart charging."
                ),
            )
    return ResultadoEscopo(dentro_escopo=True)
