"""Gera respostas para rubrica manual. Avaliacao humana obrigatoria; nao inventa scores."""
import sys, json, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.rag.pipeline import answer
parser=argparse.ArgumentParser()
parser.add_argument('--iteration', choices=['v1','v2'],required=True)
parser.add_argument('--model',default='qwen3:8b')
a=parser.parse_args()
cases=json.loads((ROOT/'evals/rag_eval_set.json').read_text())
rows=[]
for case in cases:
    try:
        result=answer(case['question'],model=a.model,version=a.iteration,k=3 if a.iteration=='v1' else 4,collection=f'chargegrid_{a.iteration}')
        rows.append({'question':case['question'],'answer':result['answer'],'sources':result['sources'],'contexts':result['contexts'],'faithfulness':None,'answer_relevancy':None,'review_notes':'PENDENTE: avaliacao humana'})
    except Exception as exc:
        rows.append({'question':case['question'],'error':str(exc),'faithfulness':None,'answer_relevancy':None})
out=ROOT/'evals'/f'results_{a.iteration}_{a.model.replace(":","_")}.json'
out.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(f'Resultados brutos salvos em {out}; atribua notas manualmente conforme evals/RUBRICA.md')
