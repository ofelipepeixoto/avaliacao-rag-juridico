# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
"""Consume a hash-pinned lexical replay; no inference or legal endorsement."""
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from metricas import retrieval_metrics


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',', ':'),allow_nan=False).encode()


def _pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Campo JSON duplicado.')
        result[key]=value
    return result


def load_package(path, expected_sha):
    if not isinstance(expected_sha,str) or not re.fullmatch('[0-9a-f]{64}',expected_sha):
        raise ValueError('Hash esperado obrigatório.')
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Arquivo regular obrigatório.')
    with path.open('rb') as stream:raw=stream.read(1024*1024+1)
    if len(raw)>1024*1024:raise ValueError('Pacote excede limite.')
    package=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Número inválido.')))
    if hashlib.sha256(canonical(package)).hexdigest()!=expected_sha:raise ValueError('Hash do pacote divergente.')
    return package


def review(package):
    if type(package) is not dict or set(package)!={'schema','corpus','cases','replay'} or package['schema']!='radar-legislative-package/v1':
        raise ValueError('Contrato de pacote inválido.')
    documents,cases,replay=package['corpus'],package['cases'],package['replay']
    if not isinstance(documents,list) or not 1<=len(documents)<=500 or not isinstance(cases,list) or not 1<=len(cases)<=200:
        raise ValueError('Limites de documento/caso inválidos.')
    if replay['schema']!='radar-legislative-replay/v1' or replay['mode']!='offline_lexical' or replay['authorization_to_execute'] is not False or replay['synthetic_only'] is not True:
        raise ValueError('Somente replay sintético sem autorização é aceito nesta etapa.')
    if hashlib.sha256(canonical(documents)).hexdigest()!=replay['corpus_sha256'] or hashlib.sha256(canonical(cases)).hexdigest()!=replay['cases_sha256']:
        raise ValueError('Hash do corpus ou casos divergente.')
    by_id={};families={};texts={}
    for d in documents:
        if d['id'] in by_id or type(d['synthetic']) is not bool or not d['synthetic']:
            raise ValueError('ID repetido ou corpus real fora do escopo.')
        if hashlib.sha256(d['text'].encode()).hexdigest()!=d['text_sha256']:
            raise ValueError('Texto alterado.')
        if families.setdefault(d['family_id'],d['split'])!=d['split'] or texts.setdefault(d['text_sha256'],d['split'])!=d['split']:
            raise ValueError('Família/texto cruza splits.')
        by_id[d['id']]=d
    case_ids={c['id'] for c in cases};rows={r['id']:r for r in replay['rows']}
    if len(case_ids)!=len(cases) or len(rows)!=len(replay['rows']) or set(rows)!=case_ids:
        raise ValueError('Cobertura dos casos divergente.')
    grouped={s:[] for s in ['train','validation','test']}
    for c in cases:
        row=rows[c['id']]
        if c['split'] not in grouped or row['esperado']!=c['expected']:
            raise ValueError('Split ou gabarito alterado.')
        for selected in [row['esperado'],row['obtido']]:
            if selected is None:continue
            if selected not in by_id:raise ValueError('Referência inexistente.')
            d=by_id[selected]
            for value in [d['valid_from'],c['as_of']]:
                if date.fromisoformat(value).isoformat()!=value:raise ValueError('Data não canônica.')
            if d['valid_until'] and date.fromisoformat(d['valid_until']).isoformat()!=d['valid_until']:raise ValueError('Data não canônica.')
            if d['split']!=c['split'] or d['kind']!=c['kind'] or d['house']!=c['house'] or not d['valid_from']<=c['as_of'] or (d['valid_until'] and c['as_of']>=d['valid_until']) or (c['kind']=='law' and d['status']!='enacted'):
                raise ValueError('Referência fora do escopo/versão.')
        if row['obtido'] is None:
            if row['citation'] is not None:raise ValueError('Citação sem resultado.')
        else:
            d=by_id[row['obtido']]
            expected={k:d[k] for k in ['id','family_id','version','house','kind','source_url','text_sha256']}
            expected.update(start=0,end=len(d['text']),review_status='pending')
            if row['citation']!=expected:raise ValueError('Citação divergente ou aprovação indevida.')
        grouped[c['split']].append(row)
    return {'schema':'radar-legislative-evaluation/v1','mode':'replay_consumption_only','synthetic_only':True,
            'corpus_sha256':replay['corpus_sha256'],'cases_sha256':replay['cases_sha256'],
            'metrics_by_split':{s:retrieval_metrics(rows) for s,rows in grouped.items()},
            'legal_correctness_verified':False,'generated_answer_evaluated':False,'authorization_to_execute':False,
            'limits':['Synthetic replay; no new retrieval or inference executed here.','Source URLs and dates are declared fixture metadata.','Hashes bind bytes, not truth or human approval.']}


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('package',type=Path)
    parser.add_argument('--expected-sha256',required=True)
    args=parser.parse_args()
    try:result=review(load_package(args.package,args.expected_sha256))
    except (ValueError,KeyError,TypeError,OSError):
        print('Pacote inválido ou fora do escopo; conteúdo omitido.',file=sys.stderr);return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
