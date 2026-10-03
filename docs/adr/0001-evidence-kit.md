# ADR 0001 — contratos de evidência separados

Data: 2026-10-03. Estado: implementação experimental em PR; extração autorizada,
pendente de disponibilidade de criação de repositório no canal conectado.

## Decisão

Vale criar `ofelipepeixoto/radar-evidence-kit`, público, MIT, versão inicial
experimental 0.1.0: já existem dois consumidores concretos com o mesmo contrato.
O repositório conterá esta biblioteca, testes, documentação e CI. Nenhum produto
jurídico, UI, parser PDF, dados reais ou clone do SDK pertence a esse núcleo.

Enquanto a criação não estiver concluída, `packages/radar-evidence-kit` neste
repositório é a única fonte. O consumidor documental fixa um commit desta origem;
não depende de um URL de repositório inexistente. Ao extrair, mover a fonte e
trocar os pins dos dois consumidores em PRs coordenados; não manter cópias
editáveis paralelas. Não há publicação PyPI, release estável ou merge automático.

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
