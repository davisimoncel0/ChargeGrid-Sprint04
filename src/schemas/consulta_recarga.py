"""Structured output do dominio EV / ChargeGrid."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


Categoria = Literal[
    "status",
    "tarifa",
    "diagnostico",
    "consumo",
    "protocolos",
    "seguranca",
    "fora_escopo",
]


class ConsultaRecarga(BaseModel):
    """Contrato de saida da Sprint 03.

    O campo ``resposta`` e o texto que deve ser mostrado ao usuario. Os
    demais campos permitem que o sistema valide e consuma a resposta sem
    depender de texto livre.
    """

    categoria: Categoria = Field(
        description="Categoria principal da solicitacao no dominio ChargeGrid."
    )
    resposta: str = Field(
        min_length=1,
        max_length=2400,
        description="Resposta final em portugues brasileiro, objetiva e pratica.",
    )
    prioridade: int = Field(
        default=2,
        description="Prioridade operacional de 1 (baixa) a 5 (critica).",
    )
    precisa_suporte: bool = Field(
        default=False,
        description="True quando o caso precisa de suporte humano especializado.",
    )
    alerta_seguranca: bool = Field(
        default=False,
        description="True quando houver risco eletrico, acesso indevido ou outro risco de seguranca.",
    )
    proximo_passo: Optional[str] = Field(
        default=None,
        description="Proxima acao recomendada ao operador, quando aplicavel.",
    )

    @field_validator("prioridade")
    @classmethod
    def validar_prioridade(cls, valor: int) -> int:
        if not 1 <= valor <= 5:
            raise ValueError("prioridade deve estar entre 1 e 5")
        return valor
