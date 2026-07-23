# Contexto do Projeto

## O que é o TokenScope DD

O TokenScope DD é uma camada de *Decision Intelligence* para ativos tokenizados e Real-World Assets (RWAs). Seu objetivo é transformar dados públicos, documentos, métricas e sinais estruturais em análises organizadas, rastreáveis, comparáveis, explicáveis e defensáveis.

## Problema e usuários

RWAs distribuem informações críticas entre documentos jurídicos, provedores, mercados, redes blockchain e processos operacionais. Essa fragmentação dificulta due diligence consistente. O produto poderá apoiar equipes institucionais de research, risco, compliance, due diligence e comitês de investimento.

## Limites do produto

O TokenScope DD não é blockchain, corretora, carteira, custodiante, plataforma de emissão, exchange, dashboard genérico, chatbot que inventa análises ou recomendador automático de investimentos.

## Recorte inicial

- fundos tokenizados lastreados em U.S. Treasuries;
- money market funds tokenizados;
- private credit tokenizado.

## Outputs futuros

Cadastro estruturado de ativos e fontes, evidências preservadas, campos normalizados, validações, red flags, benchmark, Institutional Readiness Score, Analysis Confidence Score, Risk Passport, relatórios comparativos e Investment Committee Memo.

A pergunta orientadora é quais ativos merecem avançar para due diligence mais profunda, quais exigem cautela e quais devem ser despriorizados ou monitorados. Qualquer orientação será apoio à revisão humana, nunca recomendação de investimento.

## Arquitetura e IA

O projeto é local-first: processamento, dados, documentos, logs e outputs permanecem no ambiente local controlado. O núcleo funcionará sem IA. Uma integração futura, isolada, com a API da OpenAI poderá consultar, sintetizar e explicar resultados sustentados por evidências, sem calcular scores ou inventar fatos.

## Memória e estado atual

A fundação técnica e o ambiente Python local estão prontos. A etapa atual consolida memória estratégica privada e documentação pública segura. Uma primeira coleta exploratória histórica foi registrada, mas seus dados ainda exigem curadoria e não podem alimentar score. Não há pipeline integrado, scoring, benchmark, interface ou integração de IA implementados.
