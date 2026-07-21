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
