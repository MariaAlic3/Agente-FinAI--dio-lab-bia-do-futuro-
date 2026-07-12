# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente FinAi |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Compreender o histórico de interações passadas, dúvidas anteriores sobre produtos (CDB, Tesouro) e solicitações do cliente. |
| `perfil_investidor.json` | JSON | Identificar dados cadastrais (nome, idade, profissão), renda mensal, o perfil de risco ("moderado") e as metas ativas do usuário. |
| `produtos_financeiros.json` | JSON | Atuar como catálogo oficial de investimentos (Tesouro, CDB, LCI, Fundos) para sugerir opções estritamente adequadas ao perfil.|
| `transacoes.csv` | CSV | Extrair o histórico de receitas e despesas de outubro de 2025 para calcular o saldo real e agrupar gastos por categoria. |

> [!TIP]
> **Quer um dataset mais robusto?** Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio.

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Nenhuma modificação ou expansão foi realizada nos dados originais. Optou-se por manter a base de dados padrão fornecida pelo repositório intacta. Essa abordagem garante um ambiente de testes controlado, seguro contra o vazamento de informações sensíveis e totalmente focado no cumprimento ágil dos requisitos do desafio dentro do cronograma previsto.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos JSON e CSV localizados na pasta data/ são carregados localmente na inicialização da aplicação em Python. O script utiliza a biblioteca pandas para ler e manipular os arquivos estruturados em CSV (transacoes.csv e historico_atendimento.csv) e o módulo nativo json para decodificar os metadados de perfil e produtos.

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados não são injetados de forma bruta no System Prompt para evitar o estouro da janela de contexto do modelo local. Adota-se uma Consulta Dinâmica por Contexto:

O Python intercepta a mensagem do usuário e executa toda a lógica matemática pesada (como o cálculo do saldo líquido, somatórios de despesas por categoria e filtragem de produtos compatíveis com o perfil moderado).

O resultado numérico consolidado e exato é injetado dinamicamente no prompt de usuário (User Prompt), servindo de base de verdade para que o Ollama formule a resposta textual de maneira empática e sem julgamentos.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

Exemplo pensado na otimização de tokens sem perder informações importantes.

```
Nome: João Silva
Perfil de Risco: moderado
Saldo Atual: R$ 2.511,10
Entradas: R$ 5.000,00 | Saídas: R$ 2.488,90

Gastos por Categoria:
- moradia: R$ 1.380,00
- alimentacao: R$ 570,00
- transporte: R$ 295,00
- saude: R$ 198,00
- lazer: R$ 55,90

Metas Ativas:
- Completar reserva de emergência | Alvo: R$ 15.000,00 | Prazo: 2026-06
- Entrada do apartamento | Alvo: R$ 50.000,00 | Prazo: 2027-12

Histórico Temático: Já consultou sobre CDB, Tesouro Selic e progresso de metas.

Catálogo de Produtos (Apenas Perfil Moderado):
- Fundo Multimercado | Risco: medio | Rentabilidade: CDI + 2% | Mínimo: R$ 500,00
- CDB Liquidez Diária | Risco: baixo | Rentabilidade: 102% do CDI | Mínimo: R$ 100,00
- Tesouro Selic | Risco: baixo | Rentabilidade: 100% da Selic | Mínimo: R$ 30,00
...
```
