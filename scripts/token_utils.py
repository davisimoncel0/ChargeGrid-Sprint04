"""Utilitarios de contagem de tokens com tiktoken."""

from __future__ import annotations


def contar_tokens(texto: str, encoding_name: str = "cl100k_base") -> int:
    try:
        import tiktoken

        enc = tiktoken.get_encoding(encoding_name)
        return len(enc.encode(texto))
    except Exception:
        # Fallback somente para nao interromper scripts de diagnostico.
        # A entrega deve instalar tiktoken e usar a contagem real.
        return max(1, len(texto.split()))
