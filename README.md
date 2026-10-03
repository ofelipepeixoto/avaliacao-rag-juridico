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

## Evidências e Semantica opcional

Novo experimento isolado em [experiments/semantica](experiments/semantica/README.md),
com contratos autorais, recibos e motor simbólico opcional fixado. O baseline
lexical acima permanece independente. Veja [radar-evidence-kit](packages/radar-evidence-kit/README.md)
e a [decisão de extração](docs/adr/0001-evidence-kit.md). A elegibilidade de
citação não comprova a verdade jurídica ou o suporte semântico de uma resposta.
