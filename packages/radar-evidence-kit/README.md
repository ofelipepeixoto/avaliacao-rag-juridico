# radar-evidence-kit — experimental 0.1.0

Biblioteca **autoral de Carlos Felipe**, com núcleo Python 3.11+ sem dependências
de runtime. Dois consumidores: o experimento de `avaliacao-rag-juridico` e a
exportação opt-in de `assistente-documental-ia`. Não é um fork ou renomeação do
Semantica. Esta pasta é a fonte temporária única até a extração para um
repositório próprio; não publique duas cópias divergentes.

## Instalação e verificação local

Na raiz de `avaliacao-rag-juridico`:

```sh
python -m pip install ./packages/radar-evidence-kit
python -m unittest discover -s packages/radar-evidence-kit/tests -v
python -m unittest -v test_experimento_semantica.py
python experiments/semantica/compare_reserved.py --strict
python experiments/semantica/recibo_demo.py
```

A biblioteca não instala Semantica. O experimento padrão valida contratos e
registra a indisponibilidade do motor opcional. O baseline lexical anterior
continua em `python avaliar.py`; não há ganho de recuperação alegado.

## Contratos e escopo

`Evidence` exige exatamente os campos documentados em `modelos.py`: tenant,
projeto, documento, revisão, página, texto integral, span Unicode `[start:end]`,
SHA-256 do original e do texto, estado de revisão, rótulo de revisor e flag de
identidade. Recalcula o hash do **texto inteiro**; o ID da evidência inclui todos
esses campos. O hash do original é validado contra os bytes pelo adapter
documental, e não pelo contrato isolado. Nenhum campo é truncado ou normalizado.

`Scope` deve vir de configuração confiável da aplicação, com revisões atuais.
`check_evidence(evidence, scope)` recusa escopo/revisão divergente, revisão
pendente/rejeitada, revisor ausente e identidade não verificada. A flag só é uma
afirmação do emissor: a biblioteca não oferece login, assinatura ou autenticação.
Um dict de LLM não deve emitir aprovações, Scope ou EvidenceCheck. O modo
`require_verified_review=False` é uma política explícita de laboratório e não
verifica a identidade. O diário aceita apenas avaliações pela política padrão.

Texto: até 16 KiB UTF-8; IDs: até 256 code points; revisor: até 100; revisões e
páginas: inteiros positivos exatos (bool não é inteiro válido); Scope: até
10.000 documentos. `Evidence.from_dict` rejeita campos desconhecidos. Os registros
representam elegibilidade de citação, **não verdade jurídica ou correspondência
semântica entre uma resposta e a fonte**.

## Recibos e integridade

```python
from radar_evidence import Checkpoint, Journal, check_evidence, export_prov

# evidence e scope foram emitidos pela aplicação confiável.
journal = Journal("recibos.sqlite3", scope)
previous = Checkpoint.empty(scope)  # apenas ao iniciar um diário vazio
checkpoint = journal.append(
    evidence, check_evidence(evidence, scope),
    event_id="avaliacao-001", occurred_at="2026-10-03T12:00:00Z",
    expected_checkpoint=previous,
)
# Retenha checkpoint em um domínio independente antes da próxima operação.
journal.verify(checkpoint)
prov = export_prov(journal, checkpoint)
```

SQLite com transação `BEGIN IMMEDIATE`; sequência, hash anterior e envelope
JSON completo entram no checksum. A serialização local é versionada, com nomes
e tipos de campos, sem floats/objetos arbitrários; não alega RFC 8785. Um ID
repetido com o mesmo evento é idempotente; conteúdo divergente é recusado.
O checkpoint anterior é comparado dentro da transação, evitando sobrescrever
histórico concorrente ou truncado silenciosamente. Texto de outro tenant/projeto
não entra no diário, mesmo quando a avaliação seria negativa.

**Um checkpoint independente é obrigatório.** Apagar o fim ou reescrever toda
a cadeia pode produzir uma cadeia interna válida; a comparação com o count/head
guardado fora detecta isso. Guardar banco e checkpoint sob as mesmas permissões
não oferece essa garantia. O kit não implementa custódia, assinatura, retenção,
backup, criptografia, append-only remoto nem autoridade sobre ações.

Banco e custódia externa não têm commit distribuído. Se o banco confirmar um
append e a aplicação perder a confirmação/checkpoint, o retry com checkpoint
antigo é recusado. Reconciliar essa situação exige procedimento do operador
com seu registro independente e backup; não substitua o checkpoint apenas
recalculando a cadeia local. Retenha sempre o checkpoint mais recente.

Limites: 1.000 recibos por diário, 64 KiB por registro e profundidade JSON 8.
O append verifica a cadeia inteira: adequado a este laboratório pequeno, sem
garantia de throughput ou prazo máximo. O diário contém o texto integral;
use apenas fixtures sintéticas no Git/CI. Novos arquivos são criados com modo
0600; em POSIX o kit recusa arquivos existentes com acesso de grupo/outros,
outro proprietário ou symlinks. Use também uma pasta privada. No Windows,
configure ACLs do usuário: o kit não gerencia ACLs nem isola o runtime.

## PROV-O selecionado

O exportador original produz JSON-LD com contexto inline, `Entity` para a
evidência e `Activity` para a avaliação. `qualifiedAssociation` pertence à
Activity e aponta ao `Agent` que representa o rótulo do revisor; a flag de
identidade é preservada. Não exporta texto nem nome literal do revisor.
IDs/hashes permitem correlação e ataques de dicionário a rótulos previsíveis:
o resultado não é anonimização. A exportação não consulta URLs, RDF/SPARQL ou
contextos remotos, e não alega conformidade integral de um histórico PROV.

## Semantica opcional

`radar_evidence.semantica_adapter.evaluate_support(checks)` usa somente
`TruthMaintenanceSession`, `Rule` e `FactSupport`, com regras fixas e átomos
derivados de hashes. Entrada: 1–20 EvidenceChecks únicos. Retorno determinístico
e escopo `citation_contract_only`; nenhum texto de documento vira regra.

Snapshot esperado: `semantica-agi/semantica` versão declarada **0.7.0**, commit
`a1a8404e20bc146b481dad65cbe5dcccddae84ab`. Dez arquivos relevantes são
verificados por SHA-256 antes do import; isso **não verifica o pacote inteiro,
dependências transitivas ou a segurança do ambiente Python**. Módulos previamente
carregados, import hooks e código local precisam pertencer ao runtime confiável.
Ausência, versão/hash divergente, erro e resultado inconsistente recusam suporte. `evaluation_completed` distingue
execução concluída de recusa técnica; o experimento exige esse campo para medir
concordância, inclusive quando a elegibilidade esperada é negativa.

O orçamento de tempo rejeita resultados atrasados; não interrompe uma thread ou
import bloqueado. Para prazo rígido, isole a chamada em processo supervisionado.
Não instale o SDK completo no ambiente padrão só para usar o núcleo deste kit.
Veja o experimento e a CI para o caminho opcional mínimo efetivamente testado.

Políticas, decision recorder, SPARQL, MCP, ingestão remota, provedores, ações e
explorer do Semantica **não estão integrados**. As falhas desses componentes
identificadas na auditoria continuam sendo bloqueadores para eventual adoção;
esta entrega não afirma corrigir ou homologar o upstream inteiro.

## Autoria e licença

Código desta biblioteca: MIT, Copyright (c) 2026 Carlos Felipe. Nenhum fonte
Semantica foi copiado/vendorizado. O motor opcional é dependência de terceiro,
MIT, Copyright (c) 2026 Semantica; sua autoria, licença e versão permanecem
independentes. Hashes de arquivos e referência ao commit registram a dependência,
sem transferir autoria. Fixtures são fictícias e não representam parecer jurídico.
