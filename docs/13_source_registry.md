# Source Registry

## O que é

O Source Registry é o cadastro central das fontes conhecidas pelo TokenScope DD. Se o Asset Registry responde qual ativo está sendo analisado, o Source Registry registra de onde uma informação poderá vir.

Ele organiza identidade, classificação, formas de acesso e estado das fontes. Não coleta páginas, não baixa documentos, não valida evidências e não atribui nota numérica de confiabilidade.

## Candidato e fonte oficial

Uma fonte candidata é uma observação local ainda não confirmada. Fonte encontrada não significa fonte aprovada, e fonte cadastrada não significa pronta para coleta.

Uma fonte oficial é incluída somente por promoção explícita, depois do fornecimento de uma identidade completa e da validação de suas regras. Nenhuma promoção automática ocorre por nome conhecido, URL, domínio aparentemente oficial ou presença em um coletor antigo.

A inspeção histórica local encontrou apenas a definição estática de `RWA.xyz` em `configs/sources.example.yaml`. Ela foi preservada como candidata `DISCOVERED`. Não foi possível comprovar que essa definição pertence à run `RWA_COLLECTION_20260709_020427`.

## Fonte não é endpoint

Fonte é a origem institucional ou informacional. Endpoint é um endereço específico usado para acessar algum conteúdo dessa fonte.

Uma fonte pode ter vários endpoints, por exemplo:

- página principal;
- página de produto;
- documento;
- download;
- API;
- página de dados;
- explorador.

URL não é identidade completa. Duas fontes diferentes podem depender do mesmo endereço, e uma fonte pode mudar ou descontinuar um endpoint sem perder sua identidade histórica.

## Classificação

### Autoridade

- `PRIMARY`: origem diretamente responsável pela informação.
- `SECONDARY`: fonte independente que interpreta ou reorganiza material primário.
- `TERTIARY`: compilação ou referência derivada.
- `UNASSESSED`: nível ainda não avaliado.

Fonte secundária não é automaticamente falsa. Ela apenas cumpre um papel diferente da fonte primária.

### Oficialidade

- `OFFICIAL`: publicação atribuída à organização responsável.
- `INDEPENDENT`: fonte sem vínculo oficial declarado.
- `AGGREGATOR`: reúne dados de múltiplas origens.
- `COMMUNITY`: conteúdo mantido por comunidade.
- `UNKNOWN`: relação ainda não determinada.

Site oficial também não garante que todo conteúdo esteja atualizado. Agregador não substitui documento oficial.

### Tipos e domínios

A taxonomia distingue páginas de produto, documentos oficiais, reguladores, auditores, exploradores, documentação técnica, provedores de dados, research, notícias e outras fontes.

Domínios de informação descrevem os assuntos que a fonte poderá sustentar futuramente, como identidade, estrutura legal, taxas, liquidez, holdings, reservas, atestação, performance, operações, aspectos técnicos e rede.

## Endpoints e URLs

Cada endpoint registra papel, método de acesso, tipo de conteúdo, estado e necessidade de autenticação. `requires_auth` nunca guarda credenciais.

A URL original é preservada. Para comparação determinística, a normalização:

- remove espaços externos e fragmentos;
- converte esquema e host para minúsculas;
- remove portas HTTP/HTTPS padrão;
- trata caminho vazio e barra final de forma consistente;
- preserva a query, inclusive parâmetros assinados;
- rejeita esquemas não permitidos e credenciais embutidas;
- não executa chamada HTTP.

Endpoints locais do tipo `FILE` usam um locator separado da URL.

## Estados

Uma fonte oficial distingue:

- registro: `ACTIVE`, `INACTIVE`, `ARCHIVED` ou `REJECTED`;
- verificação: `UNVERIFIED`, `PROVISIONAL` ou `VERIFIED`;
- acesso: `UNKNOWN`, `ACCESSIBLE`, `RESTRICTED`, `UNAVAILABLE` ou `DEPRECATED`;
- prontidão: `NOT_READY`, `READY`, `BLOCKED` ou `RETIRED`.

Esses estados não são equivalentes. Uma fonte pode existir ativamente no cadastro e ainda não estar verificada ou pronta para coleta.

## Verificação e prontidão

`VERIFIED` exige nome, provedor, tipo conhecido, autoridade avaliada, oficialidade conhecida, endpoint, justificativa, referência e data de verificação.

`READY` exige registro ativo, fonte verificada, acesso disponível e endpoint ativo com método suportado. Uma fonte que exige autenticação não pode ficar pronta antes de existir integração segura.

Nenhuma fonte está `VERIFIED` ou `READY` nesta etapa.

## Relação com o Asset Registry

Fontes oficiais podem apontar somente para `asset_id` existentes no Asset Registry. Candidatos a fonte podem apontar somente para candidatos a ativo existentes, quando a relação estiver comprovada localmente.

Como o Asset Registry oficial possui zero ativos, nenhuma fonte oficial possui relação com ativos. O Source Registry não cria ativos nem promove candidatos do Asset Registry.

## Promoção

A promoção recebe explicitamente um candidato elegível e uma fonte oficial completa. A operação valida todos os registries em memória antes de retornar novas versões.

Ela não infere provedor, tipo, autoridade, oficialidade ou referências e não deixa alteração parcial em caso de erro. Nenhum candidato foi promovido nesta execução.

## Fingerprint

O fingerprint SHA-256 usa JSON canônico UTF-8. Fontes, candidatos, endpoints, domínios de informação e relações com ativos são ordenados deterministicamente, e o próprio campo de fingerprint é excluído.

Formatação e ordem de chaves do YAML não alteram o hash. Mudanças reais de conteúdo alteram. O Registry oficial vazio é válido e possui fingerprint estável.

## Como validar

```powershell
& ".\.venv\Scripts\python.exe" scripts\validate_source_registry.py --write-schema --json-output outputs\reports\TS-005_source_registry_validation.json
& ".\.venv\Scripts\python.exe" -m pytest tests\unit\source_registry\test_source_registry.py -q
& ".\.venv\Scripts\python.exe" -m pytest
```

O JSON Schema em `schemas/source_registry.schema.json` é gerado diretamente do modelo Pydantic.

## Estado atual

A TS-005 está `VALIDATED` localmente e aguarda auditoria.

- 1 candidato local `DISCOVERED`;
- 0 fontes oficiais;
- 0 fontes verificadas;
- 0 fontes prontas para coleta;
- 0 endpoints oficiais;
- 0 itens de investigação;
- validação `PASSED`, sem erros ou avisos;
- 58 testes dirigidos e 99 testes na suíte completa aprovados;
- nenhuma página acessada ou baixada;
- nenhuma fonte promovida;
- nenhum score, red flag ou benchmark.

A coleta pertence à TS-006. Conteúdo coletado futuramente ainda não significará evidência validada.
