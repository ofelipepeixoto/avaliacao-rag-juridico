# ADR 0002 — Compor propostas e preservar limites de evidência

Data: 2026-10-03. Status: experimento offline integrado; operação bloqueada.

## Decisão

Compor os pais `7d46947708ca4e95447db1045e223b5645e2e551` (Promptfoo)
e `ae6f3a777c389611976ac28da5b6d91fc2af2d7d` (contratos), originados no
main `81da91ef5e744aced9310e33058dad667caa7b03`. Preservar `avaliar.py`,
corpus, desenvolvimento e reserva originais. O evidence-kit consumidor agora
fixa o main aprovado `95f1a07e7776f666ea64086e25d05af782c72b5c`.

## Métricas e testes

`metricas.py` mede precisão/recall top-1 e abstenção com denominadores explícitos.
`diagnosticos.py` diferencia contrato de citação e anotação de suporte semântico.
Não ajustar sinônimos usando a reserva. Não aceitar relatório Promptfoo com
linhas duplicadas, expectativas alteradas, provider divergente ou erro operacional.
Vermelho de qualidade continua visível: 16/24 sucessos, oito erros de recuperação.

Docker é a referência de CI. Como este ambiente local não tinha Docker e negava
namespace de rede, libseccomp bloqueou sockets de rede, connect e io_uring em
todos os descendentes. Socketpairs Unix locais são permitidos pelo runtime
Rust/SQLite. A negação foi testada em Python e Node e por preflight antes da
avaliação completa. Esse fallback não confina o filesystem nem recursos.

## Dependências

Promptfoo 0.123.1 e lockfile são fixos. `basic-ftp` foi atualizado por override
para 6.2.1, corrigindo a cadeia do alerta de parser FTP. É major diferente da
transitiva anterior: a validação cobre somente o CLI e os dois providers locais,
sem homologar providers FTP, proxy ou outros do pacote upstream.

`npm audit --json` observou sete high antes e três high após essa mudança:
node-forge 1.4.0, jks-js e Promptfoo por propagação. Nenhum critical foi reportado.
O alerta remanescente é GHSA-86w9-cpqp-85rv, verificação de assinatura RSA.
Os três resultados são uma cadeia de dependências, não três exploits comprovados.
NPM latest consultado para node-forge era 1.4.0; não inventamos patch ou aplicamos
o downgrade automático sugerido para Promptfoo 0.116.7.

Esse lote permite exclusivamente fixtures sintéticas e providers locais
revisados em avaliação com rede efetivamente bloqueada, sem JKS/TLS ou chaves.
Ampliar providers, aceitar corpus de clientes ou operar serviço exige resolução
das advisories, revisão de dependências, isolamento e validação próprios.
Opt-out, versão fixa e scanner de segredos não tornam dependências seguras.

## Gates operacionais

Semantica segue opcional e restrito às classes/regras fixas do adapter. Políticas
e SPARQL upstream continuam bloqueados. Não autenticar pessoas a partir de flags
sintéticas; aprovação e escopo precisam vir da aplicação confiável. Elegibilidade
de citação não prova suporte semântico ou correção jurídica.

Nenhuma API paga, LLM, banco vivo, credencial, workflow n8n ou VPS foi usado neste
lote. Aprovação persistente, orçamento atômico, fontes reais e evals de geração
continuam pré-requisitos para efeitos operacionais.
