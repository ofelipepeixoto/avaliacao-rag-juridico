"""Ponte para a recuperação existente. Texto recebido como dados via stdin."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from avaliar import recuperar  # noqa: E402

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode not in {'literal', 'equivalencias'}:
        raise SystemExit('Modo não permitido')
    question = json.loads(sys.stdin.read(16385))['question']
    if not isinstance(question, str) or len(question) > 2000:
        raise SystemExit('Pergunta inválida')
    print(json.dumps({'output': recuperar(question, mode == 'equivalencias') or 'SEM_TRECHO'}))
