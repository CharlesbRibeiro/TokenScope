# TokenScope DD

Camada local-first de *Decision Intelligence* para análise institucional de ativos tokenizados e Real-World Assets (RWAs). O projeto organiza dados, documentos, métricas e evidências em análises rastreáveis, comparáveis, explicáveis e defensáveis.

## Problema e público-alvo

RWAs combinam estruturas jurídicas, operação, provedores, dados de mercado e informações on-chain dispersas. O TokenScope DD pretende reduzir essa fragmentação para apoiar equipes de due diligence, risco, research e comitês de investimento. O recorte inicial abrange fundos tokenizados lastreados em U.S. Treasuries, money market funds tokenizados e private credit tokenizado.

O produto não é blockchain, corretora, carteira, custodiante, emissora, exchange, dashboard genérico ou mecanismo automático de recomendação de investimento.

## Princípio central

> A IA explica e auxilia a consulta. O sistema calcula. As evidências sustentam. O humano decide.

O núcleo funcionará sem IA. Uma integração futura com a API da OpenAI ficará isolada em `src/tokenscope_dd/ai/` e será restrita a consulta, síntese e explicação. Ela não calculará scores nem criará fatos ou evidências.

## Arquitetura local-first

Nesta fase, execução, dados, documentos, configurações, evidências, logs e resultados permanecem no ambiente local. Não há dependência obrigatória de nuvem. O GitHub é usado somente para versionamento, colaboração e revisão, não para executar o produto.

Fluxo planejado:

`Fontes → Coleta → Dados brutos → Extração → Evidências → Normalização → Validação → Features → Score → Red Flags → Benchmark → Explicação → Risk Passport → Memo de decisão`

## Estrutura do repositório

- `docs/`: contexto, visão, estratégia, arquitetura, roadmap e decisões;
- `docs/knowledge_base/`: memória documental oficial, referências e arquivo histórico;
- `configs/`: configurações versionáveis sem segredos;
- `src/tokenscope_dd/`: código Python reutilizável;
- `scripts/`: pontos de entrada de fluxos completos;
- `notebooks/`: exploração e demonstração, sem lógica de negócio;
- `data/`: dados brutos, intermediários, processados e amostras;
- `outputs/`: execuções e relatórios locais;
- `tests/`: testes unitários e de integração;
- `logs/`: logs locais não versionados.

Consulte `docs/knowledge_base/INDEX.md` antes de trabalhar em conceitos ou decisões do produto. A memória estratégica completa fica em uma camada privada local e ignorada pelo Git; o repositório público contém somente derivados seguros. Documentos oficiais não devem ser alterados sem autorização explícita.

Documentação consolidada:

- `docs/06_strategic_context_summary.md`: síntese estratégica pública, com propostas e decisões pendentes claramente identificadas;
- `docs/07_glossary.md`: conceitos essenciais para novos colaboradores;
- `docs/08_current_state.md`: estado técnico e histórico do projeto.
- `docs/09_delivery_method.md`: metodologia Human-Governed AI Delivery;
- `docs/10_task_registry.md`: estado e dependências das tarefas TS-NNN;
- `docs/knowledge_base/INDEX.md`: catálogo público das fontes oficiais e derivados seguros.

## Estado atual e roadmap

O projeto concluiu a fundação técnica e está na fase de consolidação da memória e estratégia. As etapas seguintes estão registradas em `docs/04_roadmap.md`; ainda não existem pipeline integrado, scoring, benchmark, interface ou integração com IA.

## Preparação do ambiente

Requisitos: Windows, PowerShell e Python 3.10 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest
```

Não é necessário ativar o ambiente virtual para usar seu interpretador diretamente. O VS Code está preparado para selecionar `.venv\Scripts\python.exe` quando o repositório for aberto como workspace.

Copie `.env.example` para `.env` somente quando uma futura integração autorizada exigir configuração local. Nunca versione `.env` ou segredos.

## Avisos

Este repositório é uma POC/MVP em evolução. Seus resultados não constituem recomendação de investimento e devem ser avaliados por profissionais responsáveis com base nas evidências disponíveis.
