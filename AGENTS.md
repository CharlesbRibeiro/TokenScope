# Manual de Trabalho do Codex

Este arquivo define como o Codex deve trabalhar no TokenScope DD. A memória conceitual do produto fica em `docs/knowledge_base/`.

## Leitura obrigatória

Antes de qualquer tarefa relevante, leia:

- `README.md`;
- `docs/00_project_context.md`;
- `docs/03_architecture.md`;
- `docs/04_roadmap.md`;
- `docs/05_architecture_decisions.md`;
- `docs/06_strategic_context_summary.md`;
- `docs/07_glossary.md`;
- `docs/08_current_state.md`;
- `docs/09_delivery_method.md`;
- `docs/10_task_registry.md`;
- `docs/knowledge_base/INDEX.md`.

Antes de trabalhar com produto, arquitetura, dados, coleta, scoring, benchmark, red flags, evidências, relatórios, Risk Passport, Investment Committee Memo, metodologia, taxonomia, estratégia, OpenAI ou consulta documental:

1. leia `docs/knowledge_base/INDEX.md`;
2. identifique os documentos relevantes;
3. se existir localmente, leia `docs/knowledge_base/PRIVATE_INDEX.md` e consulte a memória aplicável em `private_official/`;
4. consulte depois `official/`;
5. use `references/` apenas como apoio;
6. não use `archive/` como referência atual;
7. informe no relatório final os documentos consultados sem revelar conteúdo privado.

A consulta à memória privada é obrigatória antes de tarefas sobre produto, estratégia, metodologia, dados, scoring, red flags, benchmark, arquitetura, Risk Passport, Investment Committee Memo, OpenAI, roadmap ou comunicação institucional.

## Prioridade documental

Em caso de conflito, use esta ordem:

1. decisão mais recente em `docs/05_architecture_decisions.md`;
2. documentos em `docs/knowledge_base/private_official/`, quando disponíveis localmente e aplicáveis;
3. documentos em `docs/knowledge_base/official/`;
4. documentação principal em `docs/`;
5. documentos em `docs/knowledge_base/references/`;
6. documentos em `docs/knowledge_base/archive/`, somente como contexto histórico.

Se a documentação for insuficiente, não invente. Registre a incerteza e apresente a decisão pendente ao usuário. Não altere documentos em `official/` sem autorização explícita.

## Dados e evidências

Nunca invente dados financeiros, jurídicos, on-chain, institucionais ou operacionais; provedores; documentos; taxas; scores ou evidências.

Todo dado extraído deve preservar, quando disponível: ativo, campo, valor, unidade, fonte, URL, data de coleta, trecho de evidência, método de extração, confiança, status de validação, versão e run ID.

Separe sempre dado bruto, dado intermediário, dado processado, evidência, hipótese, conclusão e recomendação.

## Desenvolvimento

- O projeto é local-first; não crie dependências obrigatórias de nuvem.
- Use Python 3.10 ou superior, `pathlib` e type hints quando aplicável.
- Derive caminhos a partir da raiz do repositório; evite caminhos absolutos espalhados.
- Código reutilizável fica em `src/tokenscope_dd/`; scripts executáveis ficam em `scripts/`.
- Não coloque lógica de negócio em notebooks.
- Separe entrada e saída da lógica, trate erros explicitamente e teste regras importantes.
- Prefira funções pequenas e claras; evite scripts gigantes, dependências desnecessárias e overengineering.

## Inteligência artificial

- O núcleo deve funcionar sem OpenAI.
- OpenAI não calcula score, não cria fatos, não substitui evidências e não toma a decisão final.
- A futura API será usada para consulta, síntese e explicação.
- A integração ficará isolada em `src/tokenscope_dd/ai/`.
- Não implemente OpenAI sem autorização específica.

## Segurança e preservação

- Não inclua senhas ou chaves em código, documentação, testes, configurações versionadas ou logs.
- Não versione `.env`, dados sensíveis, HTML bruto pesado, respostas pesadas de APIs, logs ou outputs grandes.
- Nunca versione o TXT privado ou `docs/knowledge_base/PRIVATE_INDEX.md`.
- Não envie memória privada a serviços externos nem a processe pela OpenAI sem autorização específica.
- Não modifique o TXT privado original, não o copie integralmente para documentação pública e não revele seu conteúdo em commits ou relatórios.
- Não apague arquivos existentes, runs anteriores ou alterações locais.
- Não sobrescreva documentos oficiais.
- Não substitua evidências sem criar nova versão.
- Não altere arquitetura sem registrar a decisão.

## Git

- Execute `git status` antes de trabalhar.
- Não faça commit, push, pull request ou troca de branch sem ordem explícita.
- Não descarte alterações locais.

## Governança da entrega

- Adote `docs/09_delivery_method.md` como metodologia operacional oficial.
- O fundador é a autoridade final; o ChatGPT planeja e audita; o Codex executa localmente e testa.
- Mantenha uma tarefa principal de implementação por vez e consulte `docs/10_task_registry.md` antes de iniciar trabalho relevante.
- Classifique a autonomia: verde para mudanças pequenas e reversíveis; amarelo para direção previamente aprovada; vermelho para ações que exigem autorização explícita.
- Commit, push, pull request, publicação, custos, exposição privada, exclusões e mudanças irreversíveis são nível vermelho.
- Separe implementação, validação, auditoria, aprovação e versionamento.
- Produza evidências antes de solicitar aprovação; uma implementação não é automaticamente aprovada ou versionada.
- Consulte a memória oficial antes de tarefas grandes e não envie documentos privados a APIs ou serviços externos.
- Atualize o estado da tarefa e `docs/08_current_state.md` ao final, sem avançar status além das evidências disponíveis.

## Relatório final obrigatório

Ao concluir uma tarefa, informe: resultado e status da tarefa; objetivo executado; arquivos criados; arquivos alterados; arquivos preservados; comandos executados; testes e evidências; critérios de aceitação; documentos consultados; riscos; pendências; estado do Git; próximo passo recomendado.
