# Consumo de replay legislativo sintético

Extensão original MIT de Carlos Felipe. Usa o contrato lexical produzido no `laboratorio-busca-rag` para ampliar a avaliação por famílias, Casas, versões e abstenção. Inspiração: [LLM Legislativo](https://github.com/BaruqueRodrigues/llm-legislativo/tree/6951114da14782ae1433a19f2c4bd1d2442f0ccb); nenhum código ou peso daquele modelo foi incorporado.

```sh
python3 -m unittest -v test_legislativo_replay.py
python3 experiments/legislativo/replay.py experiments/legislativo/fixture-package.json \
  --expected-sha256 1d9034bdd2d6448c35733664099cb0e25709fb89e282db809e1c0ebe3171e347
```

O pacote contém 34 documentos e 54 casos **fictícios**, gerados no laboratório: produção fixada por SHA em SOURCE.json. Não é recorte de leis reais. O consumidor confere schema/hashes/cobertura de IDs, família/texto entre splits, referência dentro do escopo e citação pendente. Não repete a recuperação: mede o **replay fornecido**, com as métricas top-1 e abstenção já existentes neste repositório.

As notas são separadas em treino/validação/teste; acerto na fixture desenhada para exercitar o contrato não mede generalização. Datas e status são declarações sintéticas, não interpretação de vigência. Nenhuma resposta gerada, inferência, base legal real ou validade jurídica foi avaliada. Hash fixa os bytes em relação à referência confiável que o operador fornece; não autentica origem, pessoa ou verdade do conteúdo.

Citação com review_status=approved é recusada nesta etapa. Flags de qualidade jurídica e autorização de execução permanecem false. Isso preserva o gate humano para eventual adaptação ao Assistente Documental: esta entrega não altera sua aplicação, UI ou banco. O produtor limita documentos/casos; consumidor limita JSON a 1 MiB e confere o hash esperado antes de medir. Não é uma API multiusuário nem sandbox contra corridas de arquivos.

SOURCE.json e fixture-package.json são arquivos gerados/exportados; o primeiro vincula commit do produtor e hash canônico. Código e testes são originais. Não há dependência Python nova: o suite completo usa o Evidence Kit já fixado em requirements-evidence.txt.

Validação local: 25 testes aprovados, sete novos. A CI de contratos existente passa a incluir o novo teste no job core; confirmação remota após publicação. Workflow opcional Semantica, promptfoo/Docker e produção não foram reexecutados localmente nesta mudança. Nenhum LLM, n8n ou treino foi conectado.

Rollback: remover este experimento, seu teste e a inclusão no job core. Nenhuma migração ou estado persistente. O contrato entre repositórios usa JSON/hash e commits fixados, sem stack nativa e sem depender do merge de outras PRs abertas.
