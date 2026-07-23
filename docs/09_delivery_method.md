# Metodologia de Entrega

Versão pública estruturada da metodologia operacional oficial do TokenScope DD.

- Fonte oficial: `docs/knowledge_base/official/TOKENSCOPE DDMETODOLOGIA OFICIAL DE.txt`
- Versão da fonte: `1.0`
- Classificação: `OFFICIAL`
- Status: vigente

Este documento organiza a metodologia em Markdown sem substituir o TXT original. Em caso de dúvida, prevalecem a decisão explícita mais recente do fundador, as decisões arquiteturais vigentes e a fonte oficial.

## Human-Governed AI Delivery

O TokenScope DD é desenvolvido com assistência de IA e governança humana. A responsabilidade permanece com o fundador, e a tecnologia amplia planejamento, execução, testes e produção de evidências.

Princípios:

- o fundador define direção, limites e responsabilidade;
- o ChatGPT amplia análise, arquitetura e supervisão;
- o Codex executa localmente, testa e produz evidências;
- o Git registra somente o que foi aprovado.

No produto: **a IA explica; o sistema calcula; as evidências sustentam; o humano decide.**

## Papéis e autoridade

### Fundador

É a autoridade final. Define visão, problema, prioridades, limites, classificação pública ou privada, riscos aceitos, custos, metodologia, publicação e aprovação final. Avalia principalmente utilidade, coerência, compreensão, risco e prioridade.

### ChatGPT

Atua como diretor de produto, arquiteto, planejador e auditor. Transforma intenção em requisitos, compara alternativas, define escopo, arquitetura, contratos, riscos, critérios e testes, prepara especificações para o Codex e audita as entregas.

Não aprova sozinho publicação, exposição privada, custos, exclusões irreversíveis, metodologia definitiva, interpretação jurídica ou recomendação financeira.

### Codex

Atua como executor local no VS Code. Inspeciona o estado real, consulta documentos, preserva mudanças, executa apenas o escopo autorizado, cria ou altera arquivos, testa, verifica segurança e entrega evidências e relatório técnico.

Não decide sozinho estratégia, metodologia, pesos, publicação, exposição privada, uso de APIs pagas, exclusões, mudanças irreversíveis, commit ou push.

### Git e GitHub

Preservam histórico, versões, comparação, recuperação e rastreabilidade. GitHub não é o ambiente de execução. Somente conteúdo aprovado e seguro pode ser publicado.

## Níveis de autonomia

### Verde — autonomia alta

Abrange mudanças pequenas, reversíveis e compatíveis com a arquitetura, como testes, correções simples, formatação, documentação e refatoração sem mudança de comportamento.

Não autoriza publicação, exclusão de dados, alteração metodológica, custos ou exposição privada.

### Amarelo — aprovação de direção

Exige recomendação e aprovação do fundador antes da execução. Abrange novos módulos ou fluxos, modelo de dados, bibliotecas relevantes, arquitetura, contratos, roadmap, armazenamento e metodologias de validação.

A decisão deve apresentar tema, recomendação, motivo, risco, alternativa e escolha solicitada.

### Vermelho — aprovação explícita

Nada é executado sem autorização clara. Inclui commit, push, pull request, publicação, API paga, chaves, exclusão, alteração de histórico, migração destrutiva, metodologia ou pesos definitivos, envio de documentos privados, afirmações jurídicas, recomendação financeira, privilégios administrativos e mudanças de segurança.

## Fluxo oficial

1. O fundador declara a intenção.
2. O ChatGPT investiga o problema e propõe solução, arquitetura, riscos e opções.
3. O fundador aprova a direção quando necessário.
4. O ChatGPT prepara a especificação para o Codex.
5. O Codex inspeciona o ambiente e implementa localmente.
6. O Codex testa, reúne evidências e entrega relatório técnico.
7. O ChatGPT audita a entrega.
8. O fundador aprova, solicita correção, reprioriza ou interrompe.
9. O Codex versiona somente após autorização explícita.
10. O estado e o registro da tarefa são atualizados.

Fluxo resumido:

`INTENÇÃO → INVESTIGAÇÃO → PROPOSTA → APROVAÇÃO DE DIREÇÃO → ESPECIFICAÇÃO → EXECUÇÃO → TESTES E EVIDÊNCIAS → AUDITORIA → APROVAÇÃO FINAL → VERSIONAMENTO`

## Estrutura de uma tarefa

Cada tarefa deve possuir identificador `TS-NNN`, objetivo, valor esperado, escopo, fora do escopo, dependências, documentos, arquitetura, arquivos, entradas, saídas, regras, riscos, critérios de aceitação, testes, autonomia e decisões humanas necessárias.

Estados possíveis:

`PLANNED → READY → IN_PROGRESS → IMPLEMENTED → VALIDATED → AUDITED → APPROVED → VERSIONED`

`BLOCKED` pode ser usado quando não há avanço seguro possível.

`IMPLEMENTED` não significa `APPROVED`. Uma tarefa importante não é concluída apenas porque o executor declarou sucesso.

## Gates

1. **Escopo aprovado:** problema, objetivo, entrega, exclusões, dependências e documentos claros.
2. **Arquitetura aprovada:** localização, módulos, contratos, entradas, saídas e responsabilidades claros.
3. **Implementação concluída:** mudanças e preservações identificadas, sem alterações não autorizadas.
4. **Qualidade aprovada:** testes, validações, rastreabilidade, segurança e ausência de regressão.
5. **Revisão funcional:** utilidade, coerência, clareza, qualidade do output e aderência ao usuário.
6. **Versionamento:** somente após aprovação, com revisão do diff, segurança, commit, push e atualização do registro.

## Evidências

Toda aprovação deve se apoiar em evidências proporcionais ao risco: testes, exemplos, outputs, métricas, hashes, diffs, logs controlados, schemas válidos, rastreabilidade, critérios de aceitação, ausência de segredos e validação humana.

O relatório do Codex deve registrar resultado, status, objetivo, documentos consultados, arquivos criados/alterados/preservados, comandos, testes, critérios de aceitação, riscos, pendências, Git e próximo passo.

## Uma tarefa principal por vez

Por padrão, existe uma tarefa principal de implementação ativa. Trabalho paralelo só é permitido quando for independente, não alterar os mesmos arquivos, não disputar contratos e não criar estados conflitantes.

Mudanças complexas devem ser decompostas. Scoring, por exemplo, exige etapas separadas para dimensões, features, política de dados ausentes, normalização, pesos, motor, testes, explicação e validação.

## Implementação e versionamento

Alterar, testar, auditar, aprovar e versionar são etapas distintas. O fluxo preferencial é:

`Codex altera → Codex testa → Codex relata → ChatGPT audita → fundador aprova → Codex versiona`

Não combinar automaticamente alteração, commit e push, especialmente em metodologia, dados, arquitetura, segurança, documentos estratégicos e integrações.

## Segurança

- Trabalhar somente no workspace autorizado e segundo o princípio do menor privilégio.
- Nunca versionar segredos, chaves, dados privados, artefatos pesados ou memória estratégica privada.
- Não enviar documentos privados a APIs ou serviços externos sem autorização explícita.
- Não introduzir custos, elevar privilégios, desativar segurança ou executar exclusões destrutivas sem aprovação.
- O projeto permanece local-first.
- OpenAI será futura, opcional, isolada, configurada por `.env` e incapaz de calcular o score principal, inventar fatos, substituir evidências ou tomar a decisão final.

## Auditoria e aprovação humana

O ChatGPT audita aderência ao escopo e arquitetura, testes, segurança, riscos, regressões, overengineering, completude e documentação. Classifica a entrega como aprovada, aprovada com ressalvas, correção necessária ou bloqueada.

O fundador mantém a decisão final sobre aprovação e versionamento. Revisões desta metodologia devem preservar histórico, informar versão, mudanças e motivo, e receber aprovação do fundador.
