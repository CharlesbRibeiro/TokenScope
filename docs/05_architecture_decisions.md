# Decisões Arquiteturais

Este registro reúne decisões vigentes. Novas decisões devem incluir data, contexto e consequências; em conflito documental, a decisão mais recente neste arquivo prevalece.

## 2026-07-20 — Fundação técnica local-first

- O projeto será desenvolvido localmente no Windows.
- VS Code será o ambiente principal e o Codex apoiará o desenvolvimento.
- `C:\Users\Usuario\Documents\RAW` é o workspace oficial.
- `C:\Users\Usuario\Documents\RAW\TokenScope` é o único repositório oficial.
- A arquitetura é local-first e não depende de nuvem nesta fase.
- GitHub é usado para versionamento e colaboração, não para execução.
- Dados e outputs ficam no filesystem local controlado pelo projeto.
- SQLite poderá ser avaliado futuramente quando houver necessidade real.
- O núcleo funciona sem IA; scores serão calculados por regras.
- A futura IA utilizará a API da OpenAI para consulta, síntese e explicação.
- A integração OpenAI será opcional e isolada em `src/tokenscope_dd/ai/`.
- Notebooks são vitrines de exploração e demonstração, não o motor do produto.
- Lógica reutilizável fica em `src/tokenscope_dd/`.
- Evidências e suas versões serão preservadas.
- A memória oficial fica em `docs/knowledge_base/official/`.
- Documentos substituídos ou antigos ficam em `docs/knowledge_base/archive/`.

## 2026-07-21 — Memória estratégica, evidências e dados exploratórios

- O repositório GitHub é público; a memória estratégica completa permanece local e privada.
- `docs/knowledge_base/private_official/` e `docs/knowledge_base/PRIVATE_INDEX.md` são ignorados pelo Git, exceto o README público de política.
- A documentação pública é derivada, resumida e revisável; não reproduz integralmente a memória privada.
- A arquitetura permanece local-first, sem dependência de nuvem nesta fase.
- OpenAI continua futura, opcional e isolada; o núcleo é independente de IA.
- Scores serão calculados deterministicamente por regras e metodologia versionadas.
- LLM poderá apoiar consulta, síntese e explicação, mas não criar fatos, evidências, scores ou decisões.
- Evidência precede conclusão, e ausência de dado deve reduzir a confiança da análise em vez de ser tratada automaticamente como neutra.
- A run `RWA_COLLECTION_20260709_020427` é registro histórico de uma coleta exploratória.
- Os dados exploratórios exigem curadoria, deduplicação e validação antes de features, red flags definitivas, benchmark ou score.

## 2026-07-22 — Human-Governed AI Delivery e sequência de tarefas

- A metodologia Human-Governed AI Delivery, versão 1.0, é a metodologia operacional oficial.
- O fundador é a autoridade final sobre direção, risco, metodologia, aprovação e publicação.
- O ChatGPT planeja, estrutura especificações e audita entregas.
- O Codex executa localmente, testa e produz evidências dentro do escopo autorizado.
- Implementação e versionamento são etapas separadas; commit e push exigem autorização explícita.
- Apenas uma tarefa principal de implementação deve permanecer ativa por vez, salvo trabalhos independentes sem conflito.
- O contexto estratégico completo permanece privado e local; a metodologia operacional pode ser pública.
- Documentos privados não podem ser enviados a APIs ou serviços externos sem autorização explícita.
- Após a auditoria e aprovação de TS-003, a próxima etapa será TS-004 — Asset Registry.
- Scoring, red flags, benchmark e OpenAI não serão implementados antes das etapas preparatórias correspondentes.
- OpenAI permanece uma camada futura, opcional e isolada do núcleo determinístico.

## 2026-07-22 — Obsidian como camada local de conhecimento

- O Obsidian foi adotado como camada local de contexto, aprendizado e preparação de conteúdo.
- O Vault oficial fica em `C:\Users\Usuario\Documents\RAW-OBISIDIAN`, fora do repositório Git.
- O repositório continua sendo a fonte oficial; notas do Vault explicam e acompanham, mas não substituem os documentos oficiais.
- O Codex deve atualizar notas relacionadas depois de tarefas relevantes e registrar uma nota de execução.
- O conhecimento acumulado poderá originar ideias de conteúdo, mas toda publicação exige aprovação explícita do fundador.
- Nesta fase não haverá sincronização, conta conectada ou plugins externos no Vault.
- Conteúdo privado permanece local, não é enviado a APIs e não é copiado para o repositório sem autorização.
