# Arquitetura

## Fluxo conceitual

```text
Fontes
  → Coleta
  → Dados brutos
  → Extração
  → Evidências
  → Normalização
  → Validação
  → Features
  → Score
  → Red Flags
  → Benchmark
  → Explicação
  → Risk Passport
  → Memo de decisão
```

Cada etapa deverá produzir artefatos identificáveis e preservar sua relação com entradas, versões e run ID. Entrada e saída serão separadas da lógica reutilizável.

## Execução local-first

Todo o fluxo será executado localmente no Windows. Dados, documentos, evidências, configurações, logs e resultados ficarão no filesystem controlado pelo projeto. Nesta fase não existem dependências de AWS, Azure, Google Cloud ou serviços gerenciados. O GitHub serve para versionamento e colaboração, não para execução.

## Áreas técnicas

- `collection/`: aquisição futura de fontes públicas;
- `processing/`: extração, limpeza, normalização e validação;
- `evidence/`: proveniência e preservação de evidências;
- `scoring/`: regras determinísticas futuras;
- `benchmark/`: comparações futuras;
- `reporting/`: outputs estruturados futuros;
- `io/`: leitura e gravação local;
- `ai/`: fronteira reservada para integração futura e opcional.

O núcleo deve operar sem IA. A futura camada OpenAI somente explicará ou sintetizará fatos e resultados fornecidos pelo sistema; não será fonte de cálculos, evidências ou decisões.
