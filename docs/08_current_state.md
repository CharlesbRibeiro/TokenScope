# Estado Atual do Projeto

## Fundação concluída

O repositório oficial está organizado em `C:\Users\Usuario\Documents\RAW\TokenScope`, com governança em `AGENTS.md`, documentação principal, base de conhecimento, estrutura modular em `src/`, testes e políticas de segurança no `.gitignore`.

## Ambiente Python

O ambiente local `.venv` usa Python 3.13.14. O pacote `tokenscope-dd` está instalado em modo editável, o VS Code possui configuração local de interpretador e pytest, e a suíte atual registra um teste aprovado. A `.venv`, caches e artefatos de build permanecem ignorados.

O ambiente oficial é Windows, VS Code e Python local. A execução é local-first, sem serviços de nuvem. OpenAI permanece futura e opcional. Pytest está disponível na `.venv`.

## Arquitetura local-first

Execução, armazenamento, dados, evidências, logs e outputs permanecem locais. GitHub é usado para versionamento e colaboração, não para execução. O núcleo não depende de nuvem nem de IA. OpenAI continua como integração futura, opcional e isolada.

## Base de conhecimento privada

A memória estratégica completa foi depositada em `docs/knowledge_base/private_official/`, protegida do Git e acompanhada por índice privado também ignorado. Documentos públicos derivados apresentam somente sínteses seguras. O TXT original não deve ser modificado, publicado ou enviado a serviços externos sem autorização explícita.

## Camada local de conhecimento no Obsidian

O Vault oficial está em `C:\Users\Usuario\Documents\RAW-OBISIDIAN`. Ele organiza explicações didáticas, estado, tarefas, decisões, execuções, aprendizados e ideias de publicação. O repositório permanece como fonte oficial. A estrutura e a documentação da TS-003A foram validadas, auditadas e aprovadas; o versionamento está autorizado e ainda pendente.

## Histórico da primeira coleta exploratória

O histórico registra a run `RWA_COLLECTION_20260709_020427`, originalmente localizada em:

`C:\Users\charl\RAW\tokenscope_dd_data_collection\outputs\RWA_COLLECTION_20260709_020427`

Esse caminho pertence ao ambiente antigo e é apenas referência histórica, não caminho operacional vigente.

Resultados registrados:

- 38 fontes configuradas;
- 37 fontes acessadas com sucesso;
- 1 fonte com falha;
- 10 ativos mapeados;
- 108 campos candidatos extraídos;
- 684 trechos de evidência;
- 136 links de documentos descobertos;
- 5 red flags iniciais.

Ativos iniciais: BUIDL, BENJI, OUSG, USDY, USYC, USTB, STBT, TBILL, CENTRIFUGE e MAPLE.

Artefatos registrados:

- `asset_master_seed.csv`;
- `source_fetch_log.csv`;
- `extracted_field_candidates.csv`;
- `keyword_evidence_snippets.csv`;
- `discovered_document_links.csv`;
- `seed_red_flags.csv`;
- `run_summary.json`.

## Limitações atuais

Os dados da primeira run são exploratórios, candidatos, não consolidados e não validados como base final. Podem conter falsos positivos de regex e exigem curadoria. Não devem alimentar score, benchmark ou conclusões institucionais nesta fase.

Não existem ainda Asset Registry, Source Registry, pipeline integrado, Evidence Layer operacional, metodologia aprovada, score, benchmark, red flags definitivas, Risk Passport, memo, integração OpenAI ou interface.

## Capacidades planejadas e não implementadas

Continuam apenas planejados: Asset Registry, Source Registry, coletor modular, Evidence Layer operacional, Institutional Readiness Score, Analysis Confidence Score, Red Flag Engine, Benchmark, OpenAI, interface e Control Tower. Nenhuma dessas capacidades deve ser tratada como disponível no estado atual.

## Etapa atual

A fundação técnica está concluída e a fase corrente consolida memória e estratégia. O repositório passa a distinguir documentação pública segura de memória estratégica privada local.

## Tarefas

- `TS-001 — Fundação do repositório — VERSIONED` no commit `0131f78`.
- `TS-002 — Ambiente Python local — VERSIONED` no commit `67e454d`.
- `TS-003 — Memória estratégica e metodologia oficial — VERSIONED` no commit `47784f8`.
- `TS-003A — Integração do Obsidian e metodologia de conhecimento — APPROVED`.
- `TS-004 — Asset Registry — PLANNED`.
- `TS-005 — Source Registry — PLANNED`.
- `TS-006 — Integração do coletor — PLANNED`.
- `TS-007 — Curadoria dos dados — PLANNED`.
- `TS-008 — Evidence Layer — PLANNED`.

O controle detalhado está em `docs/10_task_registry.md`.

## Tarefa principal atual

A TS-003A está `APPROVED` e autorizada para commit e push. Nenhuma capacidade funcional do produto foi alterada.

## Próxima etapa recomendada

Após auditoria, aprovação e eventual versionamento da TS-003A, a próxima etapa será o planejamento da TS-004 — Asset Registry. A integração segura do coletor e dos artefatos exploratórios ocorrerá somente depois dos registries de ativos e fontes. Curadoria, deduplicação, seleção de valores e Evidence Layer permanecem fases posteriores; nada disso está implementado agora.
