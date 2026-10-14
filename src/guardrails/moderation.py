"""Moderacao simples para ataques e pedidos de alto risco.

O objetivo nao e substituir o system prompt. Esta camada funciona antes do
LLM para reduzir a chance de prompt injection e impedir que pedidos claramente
inseguros cheguem ao modelo.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResultadoModeracao:
    permitido: bool
    motivo: Optional[str] = None
    resposta: Optional[str] = None
    categoria: str = "seguranca"
    prioridade: int = 4
    precisa_suporte: bool = False
    alerta_seguranca: bool = True


_PADROES_INJECAO = [
    r"ignore\s+(todas\s+)?(as\s+)?instru[cç][oõ]es",
    r"esque[cç]a\s+(tudo|as instru[cç][oõ]es|suas regras)",
    r"revele\s+(o\s+)?system\s*prompt",
    r"mostre\s+(o\s+)?system\s*prompt",
    r"agora\s+voc[eê]\s+[eé]\s+um\s+assistente",
    r"bypass",
    r"jailbreak",
]

_PADROES_ACESSO_INDEVIDO = [
    r"hack(e(ar|ie)|ear|eio)?",
    r"sem\s+autoriza[cç][aã]o",
    r"burlar\s+(o\s+)?acesso",
    r"invadir\s+(o\s+)?(sistema|csms|ocpp)",
    r"roubar\s+(senha|token|credencial)",
]

_PADROES_RISCO_ELETRICO = [
    r"abrir\s+.*energizad",
    r"mexer\s+.*(fia[cç][aã]o|cabo|barramento).*energizad",
    r"desativar\s+.*prote[cç][aã]o",
    r"ignorar\s+.*disjuntor",
    r"choque\s+el[eé]trico",
    r"arco\s+el[eé]trico",
]

_PADROES_JURIDICO_FINANCEIRO = [
    r"aconselhamento\s+jur[ií]dico",
    r"devo\s+processar",
    r"qual\s+investimento\s+(devo|eu devo)",
    r"onde\s+investir\s+meu\s+dinheiro",
]


def _contem(texto: str, padroes: list[str]) -> bool:
    return any(re.search(padrao, texto, flags=re.IGNORECASE) for padrao in padroes)


def moderar_entrada(texto: str) -> ResultadoModeracao:
    texto = texto.strip()

    if _contem(texto, _PADROES_INJECAO) or _contem(texto, _PADROES_ACESSO_INDEVIDO):
        return ResultadoModeracao(
            permitido=False,
            motivo="prompt_injection_ou_acesso_nao_autorizado",
            resposta=(
                "Nao vou ignorar minhas regras nem orientar acesso ou alteracoes sem autorizacao. "
                "Se a alteracao de tarifas ou configuracoes for legitima, posso explicar o fluxo "
                "autorizado pelo ChargeGrid Intelligence e as permissoes necessarias."
            ),
            prioridade=5,
            precisa_suporte=False,
            alerta_seguranca=True,
        )

    if _contem(texto, _PADROES_RISCO_ELETRICO):
        return ResultadoModeracao(
            permitido=False,
            motivo="risco_eletrico",
            resposta=(
                "Nao posso orientar uma intervencao eletrica de risco por chat. Isole a area e "
                "acione um tecnico eletricista habilitado para inspecionar o equipamento com os "
                "procedimentos de seguranca adequados."
            ),
            prioridade=5,
            precisa_suporte=True,
            alerta_seguranca=True,
        )

    if _contem(texto, _PADROES_JURIDICO_FINANCEIRO):
        return ResultadoModeracao(
            permitido=False,
            motivo="aconselhamento_regulado",
            resposta=(
                "Esse pedido envolve aconselhamento juridico ou financeiro, que esta fora do "
                "escopo do Chatbot GoodWe. Procure um profissional habilitado para esse tipo de "
                "orientacao. Posso ajudar com operacao de eletropostos, OCPP, MODBUS e ChargeGrid."
            ),
            prioridade=2,
            precisa_suporte=False,
            alerta_seguranca=False,
        )

    return ResultadoModeracao(permitido=True, alerta_seguranca=False, prioridade=1)
