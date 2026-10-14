"""Gera o relatorio de evolucao da Sprint 03 em PDF (maximo 5 paginas).

O script usa os resultados medidos quando os arquivos JSON existem. Quando ainda
nao foram executados, deixa os campos explicitamente como PENDENTE em vez de
inventar numeros.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "relatorio_evolucao.pdf"


def carregar_json(nome: str):
    p = ROOT / "evals" / nome
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def valor(dados, chave, sufixo=""):
    if not dados:
        return "PENDENTE"
    v = dados.get("resumo", {}).get(chave)
    if v is None:
        return "N/D"
    return f"{v}{sufixo}"


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1.5 * cm, 0.9 * cm, "FIAP x GoodWe - EV Challenge 2026 - Sprint 03")
    canvas.drawRightString(19.5 * cm, 0.9 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def main() -> None:
    sprint3 = carregar_json("sprint3_results.json")
    baseline_exec = carregar_json("baseline_results.json")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TituloCentro", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=10))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10, leading=13, spaceAfter=14))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontSize=13, leading=16, spaceBefore=5, spaceAfter=6))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontSize=11, leading=14, spaceBefore=4, spaceAfter=4))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.2, leading=12, spaceAfter=5))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Alert", parent=styles["BodyText"], fontSize=8.5, leading=11, textColor=colors.darkred, backColor=colors.whitesmoke, borderPadding=5, spaceAfter=7))

    def cell(text, bold=False):
        style = ParagraphStyle(
            name="CellBold" if bold else "Cell",
            parent=styles["Small"],
            fontName="Helvetica-Bold" if bold else "Helvetica",
            fontSize=7.4,
            leading=9.0,
        )
        return Paragraph(str(text), style)

    def wrap_table(rows):
        return [[cell(v, bold=(r == 0)) for v in row] for r, row in enumerate(rows)]

    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.45 * cm,
        rightMargin=1.45 * cm,
        topMargin=1.35 * cm,
        bottomMargin=1.35 * cm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=rodape)])

    story = []
    story += [
        Paragraph("Relatorio de Evolucao do Projeto - Sprint 03", styles["TituloCentro"]),
        Paragraph("Chatbot GoodWe - ChargeGrid Intelligence | Prompt and Artificial Intelligence", styles["Sub"]),
        Paragraph("1. Resumo da evolucao", styles["H1x"]),
        Paragraph(
            "Nas Sprints 1 e 2, o chatbot utilizava a Hugging Face Inference API com Qwen/Qwen2.5-7B-Instruct e mantinha o historico manualmente em uma lista Python. Na Sprint 03, o nucleo foi refatorado para LangChain LCEL, com ChatPromptTemplate, ChatOllama, memoria por sessao, structured output com Pydantic v2, Context Engineering com XML tagging e guardrails de seguranca.",
            styles["Bodyx"],
        ),
        Paragraph(
            "A versao legada foi preservada em src/chatbot.py para permitir o comparativo antes/depois e a reexecucao do mesmo conjunto de 8 testes usado na Sprint 2.",
            styles["Bodyx"],
        ),
        Paragraph("2. Refatoracao - decisoes tecnicas e trade-offs", styles["H1x"]),
    ]

    decisoes = [
        ["Decisao", "Implementacao", "Trade-off"],
        ["LCEL", "prompt | ChatOllama | PydanticOutputParser", "Menos codigo manual e pipeline composavel; exige dependencias LangChain."],
        ["Memoria", "RunnableWithMessageHistory + ConversationTokenBufferMemory", "Historico separado por session_id e teto de tokens; mensagens antigas podem ser descartadas."],
        ["Structured output", "ConsultaRecarga (Pydantic v2) + field_validator", "Resposta previsivel e validada; schema rigido reduz liberdade de formato."],
        ["Context Engineering", "System prompt v2 com tags XML", "Separacao mais clara entre regras e input; prompt fica um pouco maior."],
        ["Guardrails", "Validacao deterministica antes do LLM + regras no prompt", "Bloqueia ataques evidentes; nao elimina todos os ataques possiveis."],
    ]
    t = Table(wrap_table(decisoes), colWidths=[3.1 * cm, 6.7 * cm, 8.2 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("LEADING", (0, 0), (-1, -1), 9.2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [t, Spacer(1, 6), PageBreak()]

    story += [Paragraph("3. Comparativo antes/depois", styles["H1x"])]
    baseline_eval = "62,5% (5/8 adequadas; 2 parciais; 1 inadequada)"
    if baseline_exec:
        baseline_eval = f"{valor(baseline_exec, 'nota_eval_percentual', '%')}"

    comparativo = [
        ["Metrica", "Sprints 1/2 - legado", "Sprint 03 - LCEL"],
        ["Qualidade / nota no eval", baseline_eval, valor(sprint3, "nota_eval_percentual", "%")],
        ["Tokens medios por turno", valor(baseline_exec, "tokens_medios_turno_aprox"), valor(sprint3, "tokens_medios_turno_aprox")],
        ["Latencia media", valor(baseline_exec, "latencia_media_ms", " ms"), valor(sprint3, "latencia_media_ms", " ms")],
        ["Acuracia structured output", "N/A - versao sem schema", valor(sprint3, "structured_output_accuracy_percent", "%")],
        ["Prompt injection (Teste 7)", "Inadequada na Sprint 2", "Medido por evals/run_evals.py" if not sprint3 else sprint3["resultados"][6]["avaliacao"]],
    ]
    tc = Table(wrap_table(comparativo), colWidths=[5 * cm, 6.5 * cm, 6.5 * cm], repeatRows=1)
    tc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [tc, Spacer(1, 8)]

    if not sprint3 or not baseline_exec:
        story.append(Paragraph(
            "ATENCAO: este PDF foi gerado antes da execucao dos modelos neste ambiente. Os campos PENDENTE/N/D nao foram inventados. Execute 'python evals/run_baseline.py' e 'python evals/run_evals.py' no ambiente do grupo e depois 'python scripts/gerar_relatorio.py' para substituir automaticamente esta tabela pelos valores reais.",
            styles["Alert"],
        ))

    story += [
        Paragraph("Como o ganho e provado", styles["H2x"]),
        Paragraph(
            "O mesmo eval set das Sprints anteriores foi convertido para evals/eval_set.json. A Sprint 03 mede cada resposta, latencia e tokens, alem de verificar se a saida foi validada pelo schema Pydantic. O caso de memoria usa um pre-turno com erro OCPP e depois pergunta o proximo passo, preservando a continuidade de contexto.",
            styles["Bodyx"],
        ),
        Paragraph("4. Problemas encontrados e solucoes", styles["H1x"]),
    ]

    problemas = [
        ["Problema", "Decisao / solucao", "Motivo"],
        ["Prompt injection falhou na Sprint 2", "Criar moderation.py, regras de seguranca no prompt v2 e separacao XML entre regras e user_input.", "Defesa em camadas reduz dependencia de uma unica instrucao textual."],
        ["Historico manual cresce e mistura responsabilidades", "Migrar para RunnableWithMessageHistory com session_id e limite de tokens.", "Separa sessoes e controla custo/contexto."],
        ["Texto livre dificulta integracao", "Usar ConsultaRecarga + PydanticOutputParser + field_validator.", "Falhas de formato passam a ser detectadas como validacao, nao silenciosamente."],
    ]
    tp = Table(wrap_table(problemas), colWidths=[4.4 * cm, 8.2 * cm, 5.4 * cm], repeatRows=1)
    tp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.7),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [tp, Spacer(1, 8), PageBreak()]

    story += [
        Paragraph("5. Equipe e divisao de trabalho", styles["H1x"]),
        Paragraph(
            "Os nomes e RMs foram registrados a partir de integrantes.txt. A tarefa principal deve ser confirmada pelo grupo para refletir exatamente quem executou cada frente.",
            styles["Bodyx"],
        ),
    ]
    equipe = [
        ["Integrante", "RM", "Frente principal planejada"],
        ["Davi Simoncelo", "571738", "A confirmar pelo grupo"],
        ["Augusto de Souza Avila", "570839", "A confirmar pelo grupo"],
        ["Joao Pedro Sousa", "573962", "A confirmar pelo grupo"],
        ["Matheus Evangelista Silva", "568593", "A confirmar pelo grupo"],
        ["Murilo Lima de Carvalho", "570156", "A confirmar pelo grupo"],
    ]
    te = Table(wrap_table(equipe), colWidths=[6 * cm, 3 * cm, 9 * cm], repeatRows=1)
    te.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [te, Spacer(1, 10)]

    story += [
        Paragraph("Arquivos de evidencia", styles["H2x"]),
        Paragraph(
            "prompts/: versoes do system prompt e tabela de mudancas; src/chain/: builder LCEL e memoria; src/schemas/: schema Pydantic; src/guardrails/: validacao de escopo e moderacao; evals/: conjunto de testes, resultados e comparacao de modelos; docs/relatorio_modelos.md: parametros e comparacao de 2+ modelos.",
            styles["Bodyx"],
        ),
        Paragraph("Conclusao", styles["H2x"]),
        Paragraph(
            "A Sprint 03 transforma o prototipo manual em uma arquitetura conversacional mais modular e verificavel. O ganho final deve ser interpretado pelas metricas do mesmo eval set, sem esconder trade-offs de latencia ou tokens. Os resultados quantitativos sao preenchidos automaticamente pelo gerador depois da execucao real dos modelos.",
            styles["Bodyx"],
        ),
    ]

    doc.build(story)
    print(f"Relatorio gerado: {OUT}")


if __name__ == "__main__":
    main()
