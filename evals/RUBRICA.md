# Rubrica manual (fallback RAGAS)

Avaliar as mesmas perguntas em ambas as iteracoes, conferindo respostas contra trechos efetivamente recuperados.

- **faithfulness (0 a 1):** fracao das afirmacoes verificaveis da resposta sustentadas pelos trechos recuperados. Para recusa correta sem fatos inventados, atribuir 1; recusa indevida recebe 0 em answer_relevancy.
- **answer_relevancy (0 a 1):** 1 se responde integralmente ao pedido ou recusa corretamente fora do escopo; 0,5 se parcialmente; 0 se irrelevante, errada ou recusa indevida.
- Registrar notas por pergunta, justificativa, avaliador e data nos JSONs de resultados. Media aritmetica por metrica e iteracao. Nao relatar melhoria sem comprovacao.
- A equivalencia e aproximada: julgamentos humanos seguem o objetivo das metricas, mas **nao sao scores RAGAS oficiais**.
- Comparar v1 (chunks 512, overlap 80, k=3) com v2 (chunks 800, overlap 120, k=4) no mesmo conjunto. Alterar configuracao do script de avaliacao se necessario.
