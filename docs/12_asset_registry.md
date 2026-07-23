# Asset Registry

## O que é

O Asset Registry é o cadastro central de identidade dos ativos conhecidos pelo TokenScope DD. Ele existe para responder, antes de qualquer comparação ou avaliação: “qual é exatamente o ativo analisado?”.

Ele registra identidade, classificação e estado. Não executa coleta, não substitui a Evidence Layer e não calcula scores, red flags ou benchmarks.

## Candidato não é ativo oficial

Um candidato é uma observação ainda não confirmada. O cadastro de candidatos preserva o nome e o símbolo encontrados, a execução de origem e o estado da investigação.

Um ativo oficial é uma identidade canônica adicionada apenas após fornecimento explícito de dados suficientes e validação. Encontrado não significa confirmado; confirmado não significa analisado; analisado não significa aprovado.

Os oito nomes históricos — BUIDL, BENJI, OUSG, USDY, USYC, USTB, STBT e TBILL — permanecem candidatos `DISCOVERED`. Nenhum foi promovido.

## Identidade e tipos de entidade

Símbolo não é identidade: ativos diferentes podem compartilhar o mesmo símbolo. O identificador técnico `asset_id` e a chave única `asset_key`, combinados com os demais dados de identidade, evitam que o símbolo seja usado como chave exclusiva.

- Ativo: produto financeiro específico que pode entrar no Registry oficial.
- Plataforma: infraestrutura na qual produtos podem existir.
- Protocolo: conjunto de regras ou software que oferece serviços.
- Emissor: organização responsável pela emissão ou estrutura do produto.

Centrifuge e Maple estão no cadastro de investigação como `PLATFORM_OR_PROTOCOL`, com estado `PENDING`. Eles não são ativos oficiais e nenhum produto associado foi inferido.

## Campos principais

O ativo oficial contém:

- identidade: `asset_id`, `asset_key`, nomes, símbolo e aliases;
- classificação: categoria, subcategoria, tipo de produto e ativo subjacente;
- emissor: nome, razão legal e referência;
- estrutura básica: jurisdições, site, lançamento e moeda;
- redes: rede, `chain_id`, contrato, padrão do token e estado da implantação;
- estado: registro, identidade e cobertura;
- rastreabilidade: referências de fonte e justificativa de identidade;
- controle: versões, datas e notas do Registry.

Campos sem informação confiável são opcionais e permanecem nulos ou vazios; valores artificiais não são exigidos.

## Estados

Os candidatos usam `DISCOVERED`, `UNDER_REVIEW`, `PROMOTED`, `REJECTED` ou `DUPLICATE`.

Ativos oficiais distinguem:

- estado do registro: `CANDIDATE`, `ACTIVE`, `INACTIVE`, `ARCHIVED` ou `REJECTED`;
- identidade: `UNVERIFIED`, `PROVISIONAL` ou `VERIFIED`;
- cobertura: de `NOT_STARTED` até `ANALYSIS_READY`;
- implantação em rede: `ACTIVE`, `INACTIVE`, `DEPRECATED` ou `UNKNOWN`.

Um ativo só pode ser `VERIFIED` com nome oficial, emissor, categoria válida e classificada, fontes, justificativa e data de verificação. `ANALYSIS_READY` exige ainda registro ativo e identidade verificada. Mesmo nesse estado, a Evidence Layer será exigida futuramente antes de qualquer score oficial.

## Taxonomia

A taxonomia inicial, versão `1.0.0`, permite somente:

- `tokenized_us_treasuries`;
- `tokenized_money_market_funds`;
- `tokenized_private_credit`;
- `unclassified`.

`unclassified` pode ser usado provisoriamente, mas nunca com `ANALYSIS_READY`.

## Aliases, redes e contratos

Aliases são comparados de forma determinística com normalização Unicode, `casefold`, remoção de acentos apenas para comparação, tratamento simples de pontuação e espaços. O valor original é preservado. Duplicidade no mesmo ativo ou conflito entre ativos é erro.

Contrato exige uma rede nomeada. `chain_id` é normalizado como texto, endereço vazio vira nulo e a combinação rede/contrato não pode se repetir. A TS-004 não valida semanticamente endereços de blockchains e não consulta redes externas.

## Promoção segura

A promoção é explícita e atômica em memória. Ela recebe um candidato elegível e um ativo oficial completo, valida todos os registries e só então retorna as novas versões. Uma falha não deixa alteração parcial.

A promoção não infere nome oficial, emissor, categoria ou fontes e não usa apenas o símbolo. Nenhum candidato histórico foi promovido nesta execução.

## Fingerprint

O fingerprint SHA-256 representa o contexto completo dos registries. A canonicalização:

- ignora indentação e ordem de chaves do YAML;
- ordena ativos, candidatos, aliases e implantações;
- usa JSON canônico em UTF-8, com chaves ordenadas;
- exclui campos de fingerprint.

A mesma informação lógica gera o mesmo hash; uma mudança real altera o hash. O Registry oficial vazio é válido e participa de um fingerprint estável.

## Como validar

No diretório raiz do repositório:

```powershell
& ".\.venv\Scripts\python.exe" scripts\validate_asset_registry.py --write-schema --json-output outputs\reports\TS-004_asset_registry_validation.json
& ".\.venv\Scripts\python.exe" -m pytest tests\unit\registry\test_asset_registry.py -q
& ".\.venv\Scripts\python.exe" -m pytest
```

O contrato JSON em `schemas/asset_registry.schema.json` é gerado a partir do modelo Pydantic, que permanece a fonte única das regras estruturais.

## Estado atual da TS-004

`VALIDATED` localmente e aguardando auditoria.

- 8 candidatos históricos em `DISCOVERED`;
- 0 ativos oficiais;
- 2 entidades pendentes de investigação;
- validação `PASSED`, sem erros ou avisos;
- nenhuma fonte externa verificada;
- nenhum ativo pronto para análise ou score;
- nenhum score produzido.

O Registry oficial começa vazio de propósito. Verificação de fontes e curadoria pertencem às etapas futuras TS-005 e TS-007.
