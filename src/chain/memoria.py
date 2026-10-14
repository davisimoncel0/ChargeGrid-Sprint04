"""Memoria por sessao com limite explicito de tokens.

A Sprint pede RunnableWithMessageHistory + ConversationTokenBufferMemory. O
RunnableWithMessageHistory usa ``chat_memory`` para registrar HumanMessage e
AIMessage. Depois de cada chamada, ``podar_memoria`` aplica o mesmo principio
do TokenBuffer: remove as mensagens mais antigas quando o limite e excedido.
"""

from __future__ import annotations

import os
from typing import Dict

from langchain.memory import ConversationTokenBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models.chat_models import BaseChatModel


_MEMORIAS: Dict[str, ConversationTokenBufferMemory] = {}


def limite_tokens_padrao() -> int:
    return int(os.getenv("MAX_MEMORY_TOKENS", "1200"))


def obter_memoria(
    session_id: str,
    llm: BaseChatModel,
    max_token_limit: int | None = None,
) -> ConversationTokenBufferMemory:
    if session_id not in _MEMORIAS:
        _MEMORIAS[session_id] = ConversationTokenBufferMemory(
            llm=llm,
            memory_key="history",
            return_messages=True,
            max_token_limit=max_token_limit or limite_tokens_padrao(),
        )
    return _MEMORIAS[session_id]


def obter_historico(
    session_id: str,
    llm: BaseChatModel,
    max_token_limit: int | None = None,
) -> BaseChatMessageHistory:
    return obter_memoria(session_id, llm, max_token_limit).chat_memory


def podar_memoria(session_id: str) -> None:
    """Mantem as mensagens mais recentes dentro do teto de tokens.

    O RunnableWithMessageHistory grava diretamente em ``chat_memory``. Esta
    funcao executa a poda logo apos a resposta, preservando o comportamento
    esperado de uma ConversationTokenBufferMemory.
    """
    memoria = _MEMORIAS.get(session_id)
    if memoria is None:
        return

    mensagens = memoria.chat_memory.messages
    limite = memoria.max_token_limit
    try:
        total = memoria.llm.get_num_tokens_from_messages(mensagens)
        while total > limite and len(mensagens) > 2:
            # Remove primeiro um par antigo (usuario + assistente) quando possivel.
            del mensagens[:2]
            total = memoria.llm.get_num_tokens_from_messages(mensagens)
    except Exception:
        # Fallback conservador se o backend nao oferecer contagem de tokens.
        while len(mensagens) > 12:
            del mensagens[:2]


def limpar_sessao(session_id: str) -> None:
    _MEMORIAS.pop(session_id, None)


def limpar_todas_sessoes() -> None:
    _MEMORIAS.clear()
