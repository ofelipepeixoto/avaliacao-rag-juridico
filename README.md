# Avaliação de recuperação em contrato fictício

Experimento autoral para medir a **seleção de trechos** de um contrato fictício. Não usa dados de clientes, modelo de IA, embeddings ou API. A avaliação do texto gerado por um modelo será uma etapa distinta; este repositório ainda não é RAG completo.

## Reproduzir

Com Python 3, sem dependências externas:

```bash
python avaliar.py
python -m unittest -v test_avaliar.py
```

O workflow executa ambos em cada alteração. O corpus está em `dados/contrato_ficticio.json`. As perguntas de desenvolvimento e reserva ficam em arquivos distintos. A reserva deve ser mantida sem ajustar as equivalências com base nela.

## Método

Para cada pergunta, registrar a cláusula esperada ou `null` quando nenhuma sustenta a resposta. Comparar com a cláusula selecionada pela busca. Medir acerto total e por categoria: pergunta direta, paráfrase, informação ausente e trecho relacionado mas insuficiente. Uma cláusula sobre rescisão **não** responde automaticamente ao valor de uma multa.

As equivalências `começa → início` e `cancelar → rescisão` foram escolhidas no conjunto de desenvolvimento. O resultado na reserva é uma medição separada, não uma validação estatística: quatro casos são insuficientes para extrapolar.

## Relação com os outros projetos

- [Assistente documental](https://github.com/ofelipepeixoto/assistente-documental-ia): protótipo que motivou esta investigação.
- [Laboratório de busca](https://github.com/ofelipepeixoto/laboratorio-busca-rag): comparação didática com seis perguntas; este projeto acrescenta categorias de erro e uma reserva separada.

## Referências de estudo

- [LlamaIndex — avaliação de recuperação](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/evaluating/usage_pattern_retrieval.md).
- [OpenAI Evals](https://github.com/openai/evals).

O código e os dados deste repositório são originais; as referências foram usadas para orientar o método.

## Promptfoo opcional, sem rede durante a avaliação

A integração usa **Promptfoo 0.123.1**, fixado em `package-lock.json`. Os únicos
providers configurados são duas instâncias de `promptfoo/provider.cjs`, que
executam o `recuperar` Python existente via stdin e `execFileSync`, sem shell.
Não há LLM, julgador remoto, dados de clientes, chave ou API paga.

```sh
npm ci
npm test
docker pull node@sha256:64af3819f9275802414d7cdc38c27e9d82bd564dec4d4da87d008255d36c63b4
npm run eval:offline
```

Requer Docker e Node 24 para instalação/teste local. O pull e `npm ci` acessam
registros públicos **antes** da avaliação; não execute diretamente `npx promptfoo`.
O runner monta apenas este repositório como somente leitura, não repassa variáveis
ou credenciais do host, usa tmpfs e roda com `--network none`, sem capabilities.
Antes de avaliar, confere que só existe loopback e que TCP e DNS externos falham.

**Opt-out não garante ausência de rede.** O código instalado em
`node_modules/promptfoo/dist/src/telemetry-*.js` ainda chama `sendEvent` em
`recordTelemetryDisabled`, e esse caminho chama `fetchWithProxy` mesmo com opt-out.
As flags são auxiliares; o bloqueio efetivo é o namespace de rede do contêiner.
Não montamos Docker socket nem diretórios pessoais. Somente fixtures sintéticas.

As 12 perguntas existentes são avaliadas pelos dois providers. As asserções
`equals` mantêm as expectativas originais e as falhas jurídicas aparecem como
falhas: desenvolvimento literal 5/8, equivalências 7/8; reserva 2/4 para ambos.
Total: **16 sucessos e 8 falhas de qualidade em 24 avaliações**, zero erros de
provider na execução verificada. A CI exige paridade com o Python e ausência de
erros de execução, não 100% de qualidade. Um exit 100 do Promptfoo só é aceito
após conferir cada resposta e cada resultado de asserção contra a implementação.
Não há alegação de avaliação de respostas geradas ou validação jurídica real.

Configuração gerada e relatório detalhado ficam no tmpfs, descartados ao encerrar;
o log imprime as taxas por conjunto e método. A reserva não foi usada para ajustar
o recuperador. Não adicionamos provider arbitrário ou asserções com LLM.

Integração e testes originais do projeto, com assistência de IA.
[Promptfoo](https://github.com/promptfoo/promptfoo) pertence aos autores upstream
(licença MIT no pacote instalado); dependências mantêm suas próprias licenças.
Nenhum código do motor foi copiado como autoria deste projeto.

## Evidências e Semantica opcional

Novo experimento isolado em [experiments/semantica](experiments/semantica/README.md),
com contratos autorais, recibos e motor simbólico opcional fixado. O baseline
lexical acima permanece independente. Veja [radar-evidence-kit](https://github.com/ofelipepeixoto/radar-evidence-kit)
e a [decisão de extração](docs/adr/0001-evidence-kit.md). A elegibilidade de
citação não comprova a verdade jurídica ou o suporte semântico de uma resposta.

Instale a biblioteca com `python -m pip install --no-deps -r requirements-evidence.txt`.
O arquivo fixa um commit do repositório separado; este consumidor contém o
experimento e seus gates, enquanto as fontes e testes da biblioteca ficam no kit.

## Integração das duas propostas e métricas

As propostas Promptfoo (`7d46947`) e contratos (`ae6f3a7`) foram compostas
explicitamente, preservando o baseline e as reservas. O job Promptfoo instala
o evidence-kit antes de descobrir a suíte conjunta; o job lexical continua
sem dependências externas.

```sh
python3 metricas.py
python3 experiments/semantica/diagnosticos.py  # requer o núcleo evidence-kit fixado
```

Precision@1 divide citações corretas por citações emitidas; recall@1 divide
citações corretas por perguntas com documento esperado. Uma citação ao documento
errado conta falso positivo e perda da citação esperada. As métricas de abstenção
medem quando não retornar trecho é correto. Denominador zero aparece como `null`.
Na reserva original, ambos os métodos têm precision@1 **0,5**, recall@1 **0,5**
e falso positivo em **1/2** perguntas sem suporte. São quatro casos sintéticos,
sem garantia estatística nem avaliação de resposta gerada.

O contrato passa suas 13 fixtures: cinco elegíveis e oito negativas recusadas.
Entretanto, **4/5 citações elegíveis acompanham claims anotados sem suporte**
(insuficiência, negação, valor trocado e conflito). Isso demonstra por que
elegibilidade de citação não prova entailment. Identidade, tenant e revisão são
inputs sintéticos confiáveis; não é teste de autenticação ou cobertura de ataques.

Em Linux sem Docker, existe um fallback com libseccomp:

```sh
python3 promptfoo/run_seccomp.py --output /tmp/radar-promptfoo-results.json
```

Ele nega criação de sockets de rede, conexões e io_uring no kernel, incluindo
descendentes Node/Python; preflight e regressões conferem o bloqueio. Socketpairs
Unix locais ficam permitidos para o runtime Rust/SQLite. Não é sandbox de arquivos
ou recursos: use somente os providers locais revisados e fixtures sintéticas.
O runner Docker permanece o caminho de CI com montagem somente leitura e limites.
Neste ambiente local não havia Docker; a avaliação completa foi validada pelo
fallback, com 16 sucessos, oito falhas de qualidade e nenhum erro de provider.

Semantica continua experimento opcional restrito. Falhas upstream de políticas
e SPARQL bloqueiam adoção operacional e não foram corrigidas por esta composição.

## Controle de segredos

Gitleaks fixado, fixtures e scan do histórico completo disponível estão
documentados em [docs/segredos-ci.md](docs/segredos-ci.md). O job privilegiado
usa apenas script/política da base confiável e lê a PR como dados; seu bootstrap
não equivale a check obrigatório já homologado.
