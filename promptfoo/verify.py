"""Vermelho na qualidade é preservado; conferir cobertura, paridade e execução."""
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from avaliar import carregar, recuperar


def verify_report(report):
    expected_cases = {(mode, split, case['pergunta']): case['esperado'] or 'SEM_TRECHO'
                      for split in ('desenvolvimento', 'reserva')
                      for case in carregar(split+'.json')
                      for mode in ('literal', 'equivalencias')}
    rows = report['results']['results']
    assert len(rows) == len(expected_cases), 'Cobertura incompleta'
    seen, summary = set(), {}
    for row in rows:
        mode = row['provider']['label']
        question = row['testCase']['vars']['question']
        split = row['testCase']['metadata']['split']
        key = (mode, split, question)
        assert key in expected_cases and key not in seen, 'Caso inesperado ou duplicado'
        seen.add(key)
        expected = expected_cases[key]
        assert row['testCase']['assert'][0] == {'type': 'equals', 'value': expected}, 'Expectativa alterada'
        actual = recuperar(question, mode == 'equivalencias') or 'SEM_TRECHO'
        assert row.get('response', {}).get('output') == actual, 'Provider divergiu do baseline'
        assert row['success'] == (actual == expected), 'Asserção não preservou falha de qualidade'
        assert row.get('failureReason', 0) != 2, 'Erro operacional de provider'
        counts = summary.setdefault(f'{split}/{mode}', {'passou': 0, 'falhou': 0})
        counts['passou' if row['success'] else 'falhou'] += 1
    assert seen == set(expected_cases), 'Cobertura incompleta'
    return summary


if __name__ == '__main__':
    path = Path(os.environ.get('RADAR_EVAL_WORK_DIR', '/tmp'))/'promptfoo-results.json'
    print(json.dumps({'rede': os.environ.get('RADAR_OFFLINE_GUARD', 'container_network_none'),
                      'resultados': verify_report(json.loads(path.read_text()))}, ensure_ascii=False, indent=2))
