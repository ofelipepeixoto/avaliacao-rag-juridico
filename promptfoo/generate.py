"""Mesmos dados e expectativas jurídicas; categorias e reserva ficam explícitas."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def config():
    cases = []
    for split in ('desenvolvimento', 'reserva'):
        for case in json.loads((ROOT/'dados'/f'{split}.json').read_text()):
            cases.append({'description': f"{split}/{case['categoria']}: {case['pergunta']}",
                          'vars': {'question': case['pergunta']},
                          'metadata': {'split': split, 'categoria': case['categoria']},
                          'assert': [{'type': 'equals', 'value': case['esperado'] or 'SEM_TRECHO'}]})
    return {'description': 'Recuperação sintética jurídica; sem geração de respostas',
            'prompts': ['{{question}}'],
            'providers': [{'id': 'file:///lab/promptfoo/provider.cjs', 'label': m, 'config': {'mode': m}}
                          for m in ('literal', 'equivalencias')],
            'tests': cases, 'sharing': False}

if __name__ == '__main__':
    Path('/tmp/promptfoo-config.json').write_text(json.dumps(config(), ensure_ascii=False, indent=2))
