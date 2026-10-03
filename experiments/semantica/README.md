# Experimento opcional Semantica

Código autoral Carlos Felipe, MIT. Semantica é dependência externa MIT; não foi copiado para este repositório. O adaptador chama somente TruthMaintenanceSession, Rule e FactSupport. Não cria Reasoner, actions, provenance store, policy, SPARQL, servidor, warehouse ou modelo. Imports de pacotes upstream podem carregar módulos transitivos; isso não é um sandbox para pacotes não confiáveis.

## Escopo do resultado

evaluate_support recebe 1–20 EvidenceChecks únicos emitidos pela aplicação confiável. Não aceita dicts/metadata arbitrária, generators ou strings como aprovação. O core verifica Evidence, Scope, revisão e flags fornecidas pelo emissor; o adaptador deriva CitationSupported para checks elegíveis e BundleSupported somente quando todos são elegíveis. Regras fixas e versionadas usam SHA-256 como argumentos, nunca texto de documento ou regra enviada pelo usuário.

O supported refere-se **apenas à elegibilidade do contrato de citação**. Não autentica revisores, valida bytes do artefato fonte, prova entailment da resposta, detecta contradições de texto ou avalia qualidade jurídica. Um chamador Python confiável pode fabricar um check formalmente válido; frozen dataclass/hashes não autenticam sua origem. Aplicações devem gerar revisão, identidade e Scope a partir de controles confiáveis.

O resultado inclui ruleset_version, claim_scope, engine_version, expected_snapshot, verified_modules, IDs e derived_claims ordenados. expected_snapshot é a origem esperada dos dez módulos em optional/source-manifest.json do kit; **não é prova da integridade de todo o pacote**. Dependência ausente, versão diferente de 0.7.0, bytes divergentes nesses arquivos, input inválido, erro de engine ou resultado tardio devolvem supported=False. Nenhum erro ecoa documentos, paths ou segredos de exceção.

evaluation_budget_ms tem default 2000, admite 10–5000 e descarta resultados que ultrapassam o orçamento nos checkpoints. Import frio do ambiente usado demorou aproximadamente 0,7 s, por isso 500 ms não era funcional nesse ambiente. Este orçamento **não interrompe** um import/call em andamento e não é deadline de processo. Para deadline rígido, o chamador deve usar worker isolado com watchdog. Além do orçamento, a contagem é limitada e as duas regras são acíclicas.

## Reproduzir sem instalar o SDK completo

Instale a biblioteca autoral pelo commit fixado deste consumidor:

    python -m pip install --no-deps -r requirements-evidence.txt
    python -m unittest -v test_experimento_semantica.py
    python experiments/semantica/compare_reserved.py --strict
    python experiments/semantica/recibo_demo.py

As fontes, testes do núcleo e arquivos opcionais têm origem única em
[ofelipepeixoto/radar-evidence-kit](https://github.com/ofelipepeixoto/radar-evidence-kit).
Os 89 testes da biblioteca pertencem à CI desse repositório. Este consumidor
mantém seis gates específicos, fixtures e comparação com o baseline anterior.

Para reproduzir o experimento real, use o mesmo commit do kit indicado em
requirements-evidence.txt e o snapshot upstream
`a1a8404e20bc146b481dad65cbe5dcccddae84ab`. O workflow evidencias.yml registra
ambos os checkouts. Instale as dependências mínimas de
`evidence-kit/optional/requirements.txt` do checkout fixado e execute:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=semantica-upstream \
      python evidence-kit/optional/verify_minimal_imports.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=semantica-upstream \
      python -m unittest -v test_experimento_semantica.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=semantica-upstream \
      python experiments/semantica/compare_reserved.py --semantica --strict \
      --output experiments/semantica/results-reservadas.json

Os caminhos evidence-kit e semantica-upstream representam os checkouts
registrados na CI; não instale o SDK completo para esta receita. A documentação
do kit detalha a instalação independente de seu motor opcional.

Receita real verificada em **Linux/Python 3.12**. NetworkX 3.7 declara Python >=3.12, portanto esses pins não servem para um job Python 3.11. Recomenda-se CI stdlib do core em 3.11/3.12 e job real focado em 3.12. Um conjunto para 3.11 requer resolução/teste separados, não foi inventado. Este teste via PYTHONPATH não homologa instalação completa do SDK e seus pisos/extras.

Dependências obrigatórias foram identificadas por imports reais e teste de bloqueio dos demais imports externos: networkx 3.7, numpy 2.3.5, scipy 1.17.0, pydantic 2.13.5, python-dateutil 2.9.0.post0, além de annotated-types 0.8.0, pydantic-core 2.46.5, six 1.17.0, typing-extensions 4.16.0 e typing-inspection 0.4.4. Esse subconjunto deriva do init upstream de reasoning/kg; não é uma dependência do core original. Nenhum SDK cloud, LLM, requests ou rdflib foi necessário para as três classes usadas. Pins não substituem revisão de artefatos/avisos de terceiros.

## Fixtures reservadas e resultados

fixtures-reservadas.json foi definido antes da execução e não usado para ajustar equivalências/regras. Seu SHA-256 é 2f4cdd2df6cca8d5b9d4e87550276fade1e3a42936368d27997b981c213ed67e. Textos, tenants, revisores e fontes são fictícios. Claims são anotações e não entram no checker/engine. compare_reserved.py executa o avaliar.py original, sem alterar documentos, reservas ou EQUIVALENCIAS.

| Medida | Resultado observado |
|---|---|
| Baseline original, desenvolvimento | literal 5/8; equivalências 7/8 |
| Baseline original, reserva | literal 2/4; equivalências 2/4 |
| Contrato nas 13 fixtures novas | 13/13 conforme elegibilidade esperada |
| Core versus Semantica, 11 inputs válidos | 11/11 verdicts equivalentes; engine real 0.7.0 e dez módulos verificados |
| Dois inputs malformados | span inválido e metadata desconhecida recusados antes da engine |
| Contraexemplos semânticos que seguem elegíveis | 4: insuficiência, negação, valor trocado e fontes conflitantes |

Os quatro contraexemplos são uma limitação demonstrada, não quatro respostas consideradas corretas. O adaptador não melhora recuperação: multa continua falso positivo lexical, e a reserva continua 2/4. Revisão antiga, pending/rejected, identidade não verificada, documento desconhecido e tenant errado são recusados pelas regras de elegibilidade do core. Este experimento não usa RAG vetorial, scoring de qualidade jurídica ou geração de resposta.

Testes do adapter: 13 básicos e 3 reais quando ativados. Seis gates específicos do experimento ficam em test_experimento_semantica.py, fora da biblioteca reutilizável. Os testes originais de avaliar.py continuam 3/3. derived_claims e to_dict são determinísticos para o mesmo conjunto ordenado de checks; registros de execução/tempo ficam fora do resultado. results-reservadas.json registra a comparação, sem transmissão de dados externos. --strict falha com exit 1 quando o contrato ou equivalência regredir; --semantica sem engine validada falha com exit 2. Não exige acerto lexical além do baseline nem mascara seus erros.

O campo evaluation_completed só é true após a execução terminar dentro do orçamento e suas conclusões coincidirem com o contrato esperado. Versão e módulos verificados sozinhos não contam como execução concluída; --strict recusa falhas técnicas inclusive em casos cuja elegibilidade esperada é negativa.
