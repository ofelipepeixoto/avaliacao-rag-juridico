# ADR 0001 — contratos de evidência separados

Data da auditoria: 2026-10-03 (UTC). Estado: biblioteca experimental extraída
para repositório próprio em 2026-10-02 (America/Sao_Paulo); consumidores em PR.

## Decisão

Foi criado `ofelipepeixoto/radar-evidence-kit`, público, MIT, versão inicial
experimental 0.1.0: já existem dois consumidores concretos com o mesmo contrato.
O repositório contém a biblioteca, testes, documentação e CI. Nenhum produto
jurídico, UI, parser PDF, dados reais ou clone do SDK pertence a esse núcleo.

As fontes e testes foram extraídos sem alteração do commit
`2fb8059d55974795c9db7bd4fa2540d4f5af5d2a` deste laboratório. A biblioteca
em [radar-evidence-kit](https://github.com/ofelipepeixoto/radar-evidence-kit)
é a fonte única. Ambos os consumidores fixam a mesma revisão em
`requirements-evidence.txt`; a CI do experimento fixa essa revisão também no
checkout dos arquivos opcionais. A cópia anterior de `packages/radar-evidence-kit`
foi removida deste branch, preservada no histórico Git. A CI da biblioteca
cuida dos contratos e recibos; esta CI cuida dos gates e fixtures do consumidor.
Não há cópias editáveis paralelas, publicação PyPI ou merge automático.

## Motivo

Avaliar citações e exportar páginas aprovadas compartilham IDs, revisão, escopo,
hash do texto completo e estado de revisão. Um módulo autoral pequeno permite
testar essas fronteiras sem acoplar todos os consumidores ao Semantica ou às
falhas de políticas, integridade, SPARQL e operação do SDK completo.

O diário e o exportador PROV são próprios. Semantica permanece um adapter opcional
de inferência simbólica limitada; sua saída não amplia a autoridade da avaliação
original. Os contraexemplos sintéticos demonstram que uma citação elegível pode
acompanhar uma resposta com valor errado, negação errada ou conflito não resolvido.

## Critérios antes de operação

Autenticar o emissor/revisor na aplicação, isolar dados de clientes, reter
checkpoints em domínio independente, definir acesso/retencão do texto e executar
avaliação representativa. Os rótulos locais e testes fictícios não cumprem esses
critérios. Só adicionar módulos upstream após correção e nova validação específica.
