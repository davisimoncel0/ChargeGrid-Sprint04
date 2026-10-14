"""Validacao deterministica da resposta antes de exibir ao usuario.

Evita que valores tecnicos especificos nao presentes no contexto sejam tratados
como fatos. Esta camada complementa o system prompt e o Pydantic: o parser
valida a estrutura, enquanto este modulo valida alguns sinais de integridade do
conteudo textual.
"""

from __future__ import annotations

import re


_PADROES_SENSIVEIS = [
    # Porta numerica citada como configuracao tecnica.
    re.compile(r"\bporta(?:s)?(?:\s+de\s+comunica[cç][aã]o)?\s*(?:\(|:)?\s*(\d{2,5})\b", re.I),
    # Valores numericos de latencia/jitter que nao vieram do usuario/contexto.
    re.compile(r"\b(?:lat[eê]ncia|jitter)\b[^\n,.]{0,40}?\b(\d+(?:[.,]\d+)?)\s*ms\b", re.I),
    # URL de suporte potencialmente inventada.
    re.compile(r"https?://\S+|\b(?:www\.)?suporte\.goodwe\.com\b", re.I),
    # Codigos de erro genericos apresentados como exemplos concretos.
    re.compile(r"\b(?:c[oó]digo(?:s)?\s+(?:de\s+erro\s+)?)((?:OCPP)?\d{3,})\b", re.I),
]


def _normalizar(texto: str) -> str:
    return " ".join(texto.lower().split())


def _valor_veio_do_usuario(match: re.Match[str], entrada_usuario: str) -> bool:
    """Permite repetir um valor especifico quando ele foi fornecido pelo usuario."""
    trecho = _normalizar(match.group(0))
    entrada = _normalizar(entrada_usuario)
    if trecho and trecho in entrada:
        return True

    # Para regex com grupo numerico, aceita se o numero apareceu na entrada.
    if match.groups():
        valor = next((g for g in match.groups() if g), "")
        if valor and valor.lower() in entrada:
            return True
    return False


def validar_saida(texto: str, entrada_usuario: str = "") -> str:
    """Retorna a resposta original ou uma resposta segura se detectar dado suspeito."""
    for padrao in _PADROES_SENSIVEIS:
        match = padrao.search(texto)
        if match and not _valor_veio_do_usuario(match, entrada_usuario):
            return (
                "Nao ha informacao suficiente no contexto fornecido para informar "
                "portas, codigos, valores de rede ou enderecos especificos. "
                "Consulte os logs do CSMS e a documentacao oficial da GoodWe. "
                "Se o erro OCPP persistir, acione o suporte tecnico oficial."
            )
    return texto
