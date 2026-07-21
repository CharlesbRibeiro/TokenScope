# Integração futura com IA

Esta pasta está apenas reservada. Não existe cliente, chamada de API, prompt ou dependência da OpenAI nesta etapa.

Uma implementação futura e explicitamente autorizada deverá permanecer opcional e isolada aqui, com módulos `provider.py`, `openai_client.py`, `prompts.py`, `schemas.py` e `exceptions.py`. O núcleo continuará operando sem IA. A camada poderá consultar, sintetizar e explicar dados fornecidos pelo sistema, mas não calculará scores, criará fatos, substituirá evidências ou decidirá pelo usuário.

Segredos deverão existir somente no `.env` local e nunca em arquivos versionados ou logs.
