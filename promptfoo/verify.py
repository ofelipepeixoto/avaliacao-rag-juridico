"""Vermelho na qualidade é preservado; CI verifica paridade e erros de execução."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from avaliar import recuperar
report = json.loads(Path('/tmp/promptfoo-results.json').read_text())
rows = report['results']['results']
assert len(rows) == 24, len(rows)
summary = {}
for row in rows:
    mode = row['provider']['label']
    assert mode in ('literal', 'equivalencias'), mode
    question = row['testCase']['vars']['question']
    expected = row['testCase']['assert'][0]['value']
    actual = recuperar(question, mode == 'equivalencias') or 'SEM_TRECHO'
    assert row.get('response', {}).get('output') == actual, row
    assert row['success'] == (actual == expected), row
    assert row.get('failureReason', 0) != 2, row
    split = row['testCase']['metadata']['split']
    key = f'{split}/{mode}'
    counts = summary.setdefault(key, {'passou': 0, 'falhou': 0})
    counts['passou' if row['success'] else 'falhou'] += 1
print(json.dumps({'rede': 'container --network none; TCP e DNS testados', 'resultados': summary}, ensure_ascii=False, indent=2))
