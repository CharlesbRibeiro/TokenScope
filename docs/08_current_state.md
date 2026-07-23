# Estado Atual do Projeto

## Fundação e ambiente

O repositório oficial está em `C:\Users\Usuario\Documents\RAW\TokenScope`. A fundação técnica, o ambiente Python local, a memória estratégica e a integração com o Obsidian estão versionados.

O ambiente oficial usa Windows, VS Code e Python 3.13.14 em `.venv`. O pacote está instalado em modo editável e os testes usam pytest. A arquitetura permanece local-first: dados, evidências, logs e outputs ficam locais; GitHub serve ao versionamento, não à execução. OpenAI permanece futura, opcional e isolada.

## Asset Registry

A TS-004 implementou e validou localmente a primeira versão do Asset Registry:

- taxonomia inicial versionada;
- 8 observações históricas preservadas como candidatos `DISCOVERED`;
- Registry oficial válido e intencionalmente vazio;
- Centrifuge e Maple separados como entidades `PLATFORM_OR_PROTOCOL` em investigação;
- modelos Pydantic, loader YAML, validação cruzada, fingerprint SHA-256 e promoção atômica;
- JSON Schema gerado do modelo;
- script de validação, fixtures e testes unitários.

O resultado oficial da validação foi `PASSED`, sem erros ou avisos, com fingerprint `2b7004f0074402186966378373732a015ce59fe47680038ef4fc245885dcc61a`.

Os oito candidatos são BUIDL, BENJI, OUSG, USDY, USYC, USTB, STBT e TBILL. Eles não são ativos confirmados. Nenhum candidato foi promovido e nenhum dado externo foi consultado.

A implementação, a validação e a auditoria foram concluídas, o fundador concedeu aprovação final e a TS-004 foi versionada no commit `57541680d1b752e1d72114f0b193f029bdf6f2c2`.

## Limites atuais

O Asset Registry organiza identidade, classificação e estado. Ele não avalia ativos.

## Source Registry

A TS-005 implementou e validou localmente a primeira versão do Source Registry:

- taxonomia de tipos, autoridade, oficialidade, domínios e métodos de acesso;
- separação entre candidatos, fontes oficiais, endpoints e itens de investigação;
- 1 definição estática local preservada como candidato `DISCOVERED`;
- Registry oficial válido e intencionalmente vazio;
- modelos Pydantic, normalização segura de URLs, validação cruzada, fingerprint SHA-256 e promoção atômica;
- integração de validação com candidatos e ativos oficiais da TS-004;
- JSON Schema gerado do modelo, CLI, fixtures e testes.

O resultado oficial foi `PASSED`, sem erros ou avisos, com fingerprint `12c5c090af1075f4f0ff001b272e27dba5a77f72d28fd044415c73639de1a607`.

A única observação localizada foi `RWA.xyz`, já presente em `configs/sources.example.yaml`. Ela não foi acessada, verificada ou promovida, e não foi possível comprovar relação com a run histórica de 38 fontes.

A implementação e a validação foram concluídas, a auditoria foi concluída e o fundador concedeu aprovação final. A TS-005 está `APPROVED`, com versionamento ainda pendente.

Não existem ainda coletor modular integrado, curadoria oficial, Evidence Layer operacional, scoring, red flags definitivas, benchmark, Risk Passport, Control Tower, integração OpenAI ou interface.

Nenhum ativo oficial está registrado ou pronto para análise. Uma futura marcação `ANALYSIS_READY` ainda dependerá de Evidence Layer antes de qualquer score oficial.

A coleta exploratória `RWA_COLLECTION_20260709_020427` permanece apenas como referência histórica. Seus dados são candidatos não consolidados e não devem alimentar conclusões institucionais.

## Base privada e Obsidian

A memória estratégica completa permanece em `docs/knowledge_base/private_official/`, protegida do Git. Nenhum conteúdo privado foi copiado para a implementação pública.

O Vault oficial está em `C:\Users\Usuario\Documents\RAW-OBISIDIAN`. Ele explica e acompanha a fonte oficial sem substituí-la. Sync e publicação permanecem desativados.

## Registro de tarefas

- `TS-001 — Fundação do repositório — VERSIONED` (`0131f78`).
- `TS-002 — Ambiente Python local — VERSIONED` (`67e454d`).
- `TS-003 — Memória estratégica e metodologia oficial — VERSIONED` (`47784f8`).
- `TS-003A — Integração do Obsidian — VERSIONED` (`4e2a003`).
- `TS-004 — Asset Registry — VERSIONED` (`5754168`).
- `TS-005 — Source Registry — APPROVED`.
- `TS-006 — Integração do coletor — PLANNED`.
- `TS-007 — Curadoria dos dados — PLANNED`.
- `TS-008 — Evidence Layer — PLANNED`.

## Próximo passo

Versionar com segurança a TS-005 em `main`, conforme autorização explícita do fundador. A tarefa ainda não está `VERSIONED`.

## Metadados de versionamento da TS-004

- Commit: `57541680d1b752e1d72114f0b193f029bdf6f2c2`.
- Mensagem: `feat: implement deterministic asset registry`.
- Data: `2026-07-23`.
- Branch: `main`.
- Remoto: `origin`.
- Validador: `PASSED`, com 0 erros e 0 avisos.
- Testes: 40 dirigidos e 41 na suíte completa.
- Fingerprint: `2b7004f0074402186966378373732a015ce59fe47680038ef4fc245885dcc61a`.
- SHA-256 do schema: `09E67CC2DA00A5E5DFD34A4C09442A007148B413282B23C1229C3686FB288E6D`.
