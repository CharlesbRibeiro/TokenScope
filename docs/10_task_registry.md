# Registro de Tarefas

Este registro acompanha o estado real das tarefas principais. Estados não avançam sem evidências e aprovação compatíveis com `docs/09_delivery_method.md`.

| ID | Título | Objetivo | Status | Nível de autonomia | Dependências | Aprovação | Commit | Próximo passo |
|---|---|---|---|---|---|---|---|---|
| TS-001 | Fundação do repositório | Estabelecer estrutura, governança, documentação e arquitetura local-first. | `VERSIONED` | Amarelo aprovado | Nenhuma | Aprovada pelo fundador | `0131f78` | Preservar como baseline. |
| TS-002 | Ambiente Python local | Criar `.venv`, instalar dependências declaradas, configurar VS Code e validar testes. | `VERSIONED` | Amarelo aprovado | TS-001 | Aprovada e publicada | `67e454d` | Preservar como ambiente oficial. |
| TS-003 | Memória estratégica e metodologia oficial | Consolidar fontes oficiais, derivados públicos, governança e registro permanente de tarefas. | `VERSIONED` | Amarelo aprovado para execução documental; vermelho autorizado para versionamento | TS-001, TS-002 | Aprovada e publicada | `47784f8` | Preservar como baseline estratégico. |
| TS-003A | Integração do Obsidian e metodologia de conhecimento | Organizar contexto e aprendizado em um Vault local, sem substituir o repositório. | `VERSIONED` | Amarelo aprovado; vermelho autorizado para versionamento | TS-003 | Aprovada e publicada | `4e2a003` | Preservar como baseline de conhecimento. |
| TS-004 | Asset Registry | Implementar identidade, classificação e estado dos ativos, separando candidatos e entidades em investigação. | `VERSIONED` | Vermelho — versionamento explicitamente autorizado | TS-003A versionada | Aprovada e publicada | `5754168` | Preservar como baseline do Asset Registry. |
| TS-005 | Source Registry | Definir e implementar o cadastro de fontes e sua governança. | `APPROVED` | Vermelho — versionamento explicitamente autorizado | TS-004 versionada | Auditoria concluída e aprovação do fundador concedida | — | Criar e enviar o primeiro commit da TS-005. |
| TS-006 | Integração do coletor | Integrar com segurança o coletor exploratório ao repositório atual. | `PLANNED` | A definir | TS-004, TS-005 | Pendente | — | Inventariar coletor e artefatos após os registries. |
| TS-007 | Curadoria dos dados | Deduplicar, validar e selecionar valores candidatos com rastreabilidade. | `PLANNED` | A definir | TS-006 | Pendente | — | Definir regras de curadoria e critérios de aceite. |
| TS-008 | Evidence Layer | Estruturar evidências, confiança, hashes, fontes e referências documentais. | `PLANNED` | A definir | TS-007 | Pendente | — | Definir schema após a curadoria. |

## Evidências da TS-004

- validação oficial: `PASSED`, 0 erros e 0 avisos;
- 8 candidatos, 0 ativos oficiais e 2 entidades em investigação;
- fingerprint: `2b7004f0074402186966378373732a015ce59fe47680038ef4fc245885dcc61a`;
- 40 testes dirigidos e 41 testes na suíte completa aprovados;
- JSON Schema gerado a partir do modelo Pydantic;
- relatório local: `outputs/reports/TS-004_asset_registry_validation.json`.

A implementação, a validação e a auditoria foram concluídas, o fundador concedeu aprovação final e o primeiro commit foi aceito em `origin/main`.

## Metadados de versionamento da TS-004

- Primeiro commit: `57541680d1b752e1d72114f0b193f029bdf6f2c2`.
- Mensagem: `feat: implement deterministic asset registry`.
- Data do versionamento: `2026-07-23`.
- Branch: `main`.
- Remoto: `origin`.
- Validador: `PASSED`, com 0 erros e 0 avisos.
- Testes: 40 dirigidos e 41 na suíte completa.
- Fingerprint do Registry: `2b7004f0074402186966378373732a015ce59fe47680038ef4fc245885dcc61a`.
- SHA-256 do JSON Schema: `09E67CC2DA00A5E5DFD34A4C09442A007148B413282B23C1229C3686FB288E6D`.

## Evidências da TS-005

- validação oficial: `PASSED`, 0 erros e 0 avisos;
- 1 candidato, 0 fontes oficiais e 0 itens de investigação;
- nenhuma fonte verificada ou pronta para coleta;
- fingerprint: `12c5c090af1075f4f0ff001b272e27dba5a77f72d28fd044415c73639de1a607`;
- SHA-256 do JSON Schema: `0913A7290352A5A1B4558A10E25126DB4BB33532BFC60184D26E8AC3194B8F2E`;
- 58 testes dirigidos e 99 testes na suíte completa aprovados;
- relatórios locais em `outputs/reports/`, ignorados pelo Git.

A implementação, a validação e a auditoria foram concluídas, e o fundador concedeu aprovação final. O versionamento permanece pendente até a aceitação do commit e do push.

## Regras de manutenção

- Uma tarefa principal de implementação por vez.
- Atualizar status somente com evidências.
- Separar implementação, validação, auditoria, aprovação e versionamento.
- Registrar o hash do commit apenas quando ele existir no histórico Git.
- Não marcar tarefa como `VERSIONED` com base apenas em arquivos locais.

## Metadados de versionamento da TS-003A

- Primeiro commit: `4e2a003553daa56c27566e2ec99ca61bdec563b4`.
- Mensagem: `docs: integrate Obsidian knowledge governance`.
- Data do versionamento: `2026-07-22`.
- Branch: `main`.
- Remoto: `origin`.
