# Registro de Tarefas

Este registro acompanha o estado real das tarefas principais. Estados não devem avançar sem evidência e aprovação compatíveis com `docs/09_delivery_method.md`.

| ID | Título | Objetivo | Status | Nível de autonomia | Dependências | Aprovação | Commit | Próximo passo |
|---|---|---|---|---|---|---|---|---|
| TS-001 | Fundação do repositório | Estabelecer estrutura, governança, documentação e arquitetura local-first. | `VERSIONED` | Amarelo aprovado | Nenhuma | Aprovada pelo fundador | `0131f78` | Preservar como baseline. |
| TS-002 | Ambiente Python local | Criar `.venv`, instalar dependências declaradas, configurar VS Code e validar testes. | `VERSIONED` | Amarelo aprovado | TS-001 | Aprovada e publicada | `67e454d` | Preservar como ambiente oficial. |
| TS-003 | Memória estratégica e metodologia oficial | Consolidar fontes oficiais, derivados públicos, governança e registro permanente de tarefas. | `VERSIONED` | Amarelo aprovado para execução documental; vermelho autorizado para versionamento | TS-001, TS-002 | Aprovada e publicada | `47784f8` | Iniciar o planejamento da TS-004. |
| TS-003A | Integração do Obsidian e metodologia de conhecimento | Organizar contexto, aprendizado e preparação de publicações em um Vault local, sem substituir o repositório oficial. | `APPROVED` | Amarelo aprovado; vermelho autorizado para versionamento | TS-003 | Auditada e aprovada pelo fundador | — | Versionar somente os documentos públicos aprovados. |
| TS-004 | Asset Registry | Definir e implementar o cadastro canônico de ativos. | `PLANNED` | A definir | TS-003 versionada; TS-003A auditada e aprovada | Pendente | — | Preparar decisão de arquitetura e contrato de dados após a TS-003A. |
| TS-005 | Source Registry | Definir e implementar o cadastro de fontes e sua governança. | `PLANNED` | A definir | TS-004 | Pendente | — | Planejar após o contrato do Asset Registry. |
| TS-006 | Integração do coletor | Integrar com segurança o coletor exploratório ao repositório atual. | `PLANNED` | A definir | TS-004, TS-005 | Pendente | — | Inventariar coletor e artefatos após os registries. |
| TS-007 | Curadoria dos dados | Deduplicar, validar e selecionar valores candidatos com rastreabilidade. | `PLANNED` | A definir | TS-006 | Pendente | — | Definir regras de curadoria e critérios de aceite. |
| TS-008 | Evidence Layer | Estruturar evidências, confiança, hashes, fontes e referências documentais. | `PLANNED` | A definir | TS-007 | Pendente | — | Definir schema após a curadoria. |

## Regras de manutenção

- Uma tarefa principal de implementação por vez.
- Atualizar status somente com evidências.
- Separar implementação, validação, auditoria, aprovação e versionamento.
- Registrar o hash do commit apenas quando ele existir no histórico Git.
- Não marcar tarefa como `VERSIONED` com base apenas em arquivos locais.
