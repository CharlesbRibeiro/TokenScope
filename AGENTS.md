# Manual de Trabalho do Codex

Este arquivo define como o Codex deve trabalhar no TokenScope DD. A memória conceitual do produto fica em `docs/knowledge_base/`.

## Leitura obrigatória

Antes de qualquer tarefa relevante, leia:

- `README.md`;
- `docs/00_project_context.md`;
- `docs/03_architecture.md`;
- `docs/04_roadmap.md`;
- `docs/05_architecture_decisions.md`;
- `docs/knowledge_base/INDEX.md`.

Antes de trabalhar com produto, arquitetura, dados, coleta, scoring, benchmark, red flags, evidências, relatórios, Risk Passport, Investment Committee Memo, metodologia, taxonomia, estratégia, OpenAI ou consulta documental:

1. leia `docs/knowledge_base/INDEX.md`;
2. identifique os documentos relevantes;
3. consulte primeiro `official/`;
4. use `references/` apenas como apoio;
5. não use `archive/` como referência atual;
6. informe no relatório final os documentos consultados.

## Prioridade documental

Em caso de conflito, use esta ordem:

1. decisão mais recente em `docs/05_architecture_decisions.md`;
2. documentos em `docs/knowledge_base/official/`;
3. documentação principal em `docs/`;
4. documentos em `docs/knowledge_base/references/`;
5. documentos em `docs/knowledge_base/archive/`, somente como contexto histórico.

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
- Não apague arquivos existentes, runs anteriores ou alterações locais.
- Não sobrescreva documentos oficiais.
- Não substitua evidências sem criar nova versão.
- Não altere arquitetura sem registrar a decisão.

## Git

- Execute `git status` antes de trabalhar.
- Não faça commit, push, pull request ou troca de branch sem ordem explícita.
- Não descarte alterações locais.

## Relatório final obrigatório

Ao concluir uma tarefa, informe: resumo; arquivos criados; arquivos alterados; arquivos preservados; comandos executados; testes executados; documentos consultados; riscos; pendências; próximo passo recomendado.
