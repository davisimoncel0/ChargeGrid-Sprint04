"""Builder LCEL do Chatbot GoodWe - Sprint 03."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama

from src.guardrails import moderar_entrada, validar_escopo, validar_saida
from src.schemas import ConsultaRecarga
from .memoria import limpar_sessao, obter_historico, podar_memoria


ROOT = Path(__file__).resolve().parents[2]
PROMPT_V2 = ROOT / "prompts" / "system_prompt_v2.md"


def _ler_prompt() -> str:
    if not PROMPT_V2.exists():
        raise FileNotFoundError(
            f"System prompt nao encontrado: {PROMPT_V2}"
        )

    return PROMPT_V2.read_text(encoding="utf-8")


def _configuracao_modelo() -> dict:
    load_dotenv(ROOT / ".env")

    return {
        "model": os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud"),
        "base_url": os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ),
        "temperature": float(
            os.getenv("TEMPERATURE", "0.2")
        ),
        "top_p": float(
            os.getenv("TOP_P", "0.9")
        ),

        # Aumentado para evitar respostas cortadas.
        # O teste de tarifa estava terminando no meio da resposta.
        "num_predict": int(
            os.getenv("MAX_TOKENS", "512")
        ),
    }


def criar_chain(
    model: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
):
    """
    Monta a chain LCEL:

    ChatPromptTemplate
        |
    ChatOllama
        |
    RunnableWithMessageHistory
        |
    PydanticOutputParser

    A memoria registra HumanMessage e AIMessage antes
    da conversao final para o objeto Pydantic.
    """

    cfg = _configuracao_modelo()

    if model is not None:
        cfg["model"] = model

    if temperature is not None:
        cfg["temperature"] = temperature

    if top_p is not None:
        cfg["top_p"] = top_p

    if max_tokens is not None:
        cfg["num_predict"] = max_tokens

    # Modelo Ollama
    llm = ChatOllama(**cfg)

    # Parser Pydantic v2
    parser = PydanticOutputParser(
        pydantic_object=ConsultaRecarga
    )

    # Prompt principal
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _ler_prompt()
                + "\n\n"
                + "<structured_output>\n"
                + "{format_instructions}\n"
                + "</structured_output>",
            ),

            # Historico da conversa
            MessagesPlaceholder(
                variable_name="history"
            ),

            # Entrada atual do usuario
            (
                "human",
                "<user_input>\n"
                "{input}\n"
                "</user_input>",
            ),
        ]
    ).partial(
        format_instructions=parser.get_format_instructions()
    )

    # LCEL principal
    modelo_com_prompt = prompt | llm

    def get_session_history(session_id: str):
        return obter_historico(
            session_id,
            llm,
        )

    # Memoria por sessao
    com_memoria = RunnableWithMessageHistory(
        modelo_com_prompt,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # Parser fica depois da memoria para que a memoria
    # guarde a mensagem original do modelo.
    chain = com_memoria | parser

    return chain, llm


class ChatbotGoodWe:
    """Fachada usada pelo terminal e pelos evals."""

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:

        self.chain, self.llm = criar_chain(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

    @staticmethod
    def _resposta_guardrail(
        resposta: str,
        *,
        categoria: str = "seguranca",
        prioridade: int = 4,
        precisa_suporte: bool = False,
        alerta_seguranca: bool = True,
        proximo_passo: str | None = None,
    ) -> ConsultaRecarga:

        return ConsultaRecarga(
            categoria=categoria,
            resposta=resposta,
            prioridade=prioridade,
            precisa_suporte=precisa_suporte,
            alerta_seguranca=alerta_seguranca,
            proximo_passo=proximo_passo,
        )

    def responder(
        self,
        mensagem: str,
        session_id: str = "default",
    ) -> ConsultaRecarga:

        # -----------------------------
        # 1. Guardrail de seguranca
        # -----------------------------

        moderacao = moderar_entrada(mensagem)

        if not moderacao.permitido:
            return self._resposta_guardrail(
                moderacao.resposta
                or "Solicitacao recusada por seguranca.",
                categoria=moderacao.categoria,
                prioridade=moderacao.prioridade,
                precisa_suporte=moderacao.precisa_suporte,
                alerta_seguranca=moderacao.alerta_seguranca,
            )

        # -----------------------------
        # 2. Validacao de escopo
        # -----------------------------

        escopo = validar_escopo(mensagem)

        if not escopo.dentro_escopo:
            return self._resposta_guardrail(
                escopo.resposta
                or "Assunto fora do escopo ChargeGrid.",
                categoria="fora_escopo",
                prioridade=1,
                precisa_suporte=False,
                alerta_seguranca=False,
                proximo_passo=(
                    "Faca uma pergunta sobre operacao "
                    "de eletropostos ChargeGrid."
                ),
            )

        # -----------------------------
        # 3. Chain LCEL
        # -----------------------------

        resposta = self.chain.invoke(
            {
                "input": mensagem
            },
            config={
                "configurable": {
                    "session_id": session_id
                }
            },
        )

        # Valida a integridade do conteudo antes de exibir a resposta.
        # O Pydantic valida a estrutura; esta camada evita alguns valores
        # tecnicos especificos nao sustentados pelo contexto.
        resposta.resposta = validar_saida(resposta.resposta, mensagem)

        # Mantem memoria dentro do limite
        podar_memoria(session_id)

        return resposta

    @staticmethod
    def limpar(
        session_id: str = "default"
    ) -> None:

        limpar_sessao(session_id)