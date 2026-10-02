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
