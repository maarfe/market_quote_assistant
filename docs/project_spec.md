# Project Spec — Market Quote Assistant

## 1. Project Name

**Market Quote Assistant**

Nome interno do repositório pode ser:

**market_quote_assistant**

---

## 2. Purpose

O projeto tem como objetivo reduzir o tempo, o esforço mental e o custo envolvidos na compra de itens recorrentes de mercado, através da coleta, normalização, comparação e recomendação de opções de compra entre diferentes mercados e plataformas.

O sistema não executará compras no escopo inicial. Seu foco será exclusivamente apoiar a tomada de decisão.

---

## 3. Problem Statement

Hoje, comparar preços de itens do dia a dia exige um processo manual e repetitivo:

* acessar diferentes apps e sites
* buscar item por item
* interpretar nomes diferentes para produtos equivalentes
* comparar preços manualmente
* considerar frete, disponibilidade e mínimos de pedido

Esse processo é ineficiente, difícil de escalar e desgastante para listas recorrentes.

---

## 4. Proposed Solution

Construir um sistema capaz de:

* receber uma lista de compras padronizada
* consultar preços em múltiplas fontes
* normalizar produtos equivalentes
* comparar cenários de compra
* sugerir a melhor estratégia com base em regras claras

O sistema deve responder de forma objetiva:

* quanto custa comprar tudo em cada mercado
* qual é a melhor opção em mercado único
* qual é a melhor combinação entre mercados
* quais itens não puderam ser encontrados
* quais comparações são confiáveis e quais são apenas aproximadas

---

## 5. Initial Scope

## 5.1 In Scope for MVP

O MVP deve contemplar:

* entrada de lista de compras em formato estruturado
* coleta de preços a partir de fontes mockadas ou simples
* normalização básica de nomes de produtos
* agrupamento de ofertas equivalentes
* comparação entre mercados
* recomendação final baseada em cenários
* saída em CLI e/ou JSON

## 5.2 Out of Scope for MVP

O MVP não deve contemplar:

* login automatizado em marketplaces
* automação de checkout
* pagamento
* criação automática de carrinho
* integração complexa com apps fechados
* scraping pesado em múltiplas fontes ao mesmo tempo
* interface web
* banco de dados
* machine learning
* embeddings ou IA para matching de produtos

---

## 6. Product Principles

O projeto deve seguir os princípios abaixo:

### 6.1 Decision First

O maior valor do sistema está em apoiar a decisão, não em automatizar a compra.

### 6.2 Simple First

A primeira versão deve provar a utilidade do raciocínio antes de lidar com integrações complexas.

### 6.3 Safe Comparisons

O sistema não deve comparar produtos incompatíveis como se fossem equivalentes.

### 6.4 Explainability

Toda recomendação deve ser explicável de forma simples:

* por que um mercado foi melhor
* por que determinada combinação foi escolhida
* por que certos produtos não foram considerados equivalentes

### 6.5 Incremental Growth

A arquitetura deve permitir evolução gradual:

* de dados mockados para dados reais
* de CLI para API/web
* de regras simples para regras mais sofisticadas

---

## 7. Functional Requirements

## 7.1 Shopping List Input

O sistema deve receber uma lista de compras contendo itens desejados.

Cada item deve permitir, no mínimo:

* nome base
* quantidade desejada
* unidade esperada, quando aplicável

Exemplo conceitual:

* arroz
* leite integral
* banana

---

## 7.2 Market Offers Input

O sistema deve ser capaz de consumir ofertas de mercados a partir de coletores.

No MVP, essas ofertas poderão vir de:

* arquivos mockados
* JSON local
* fonte simples com baixo acoplamento

Cada oferta deve conter, no mínimo:

* mercado
* nome original do produto
* preço
* disponibilidade
* link opcional
* unidade/volume/peso quando identificado

---

## 7.3 Product Normalization

O sistema deve normalizar nomes e atributos de produtos para identificar equivalência entre ofertas.

A normalização inicial deve considerar:

* padronização textual
* remoção de ruídos
* extração de unidade
* extração de volume/peso
* identificação de termos relevantes e irrelevantes

---

## 7.4 Product Matching

O sistema deve classificar a relação entre item buscado e oferta encontrada.

Classificações iniciais sugeridas:

* **exact_match**: produto equivalente com alta confiança
* **adjustable_match**: produto comparável com ajuste de unidade/quantidade
* **partial_match**: produto parecido, mas com confiança limitada
* **invalid_match**: produto não equivalente

No MVP, a recomendação final deve priorizar apenas:

* exact_match
* adjustable_match

---

## 7.5 Scenario Comparison

O sistema deve calcular, no mínimo, os seguintes cenários:

### A. Best Single Market

Comprar todos os itens encontrados em um único mercado.

### B. Best Combined Option

Comprar cada item no mercado com menor custo válido.

### C. Best Final Cost Considering Delivery

Comparar cenários considerando frete.

### D. Lowest Order Count

Privilegiar praticidade, reduzindo quantidade de pedidos.

---

## 7.6 Recommendation Output

O sistema deve retornar:

* preços por item
* total por mercado
* total com frete, quando houver
* itens ausentes
* melhor cenário identificado
* justificativa da recomendação

---

## 8. Non-Functional Requirements

## 8.1 Code Quality

Todo o projeto deve seguir:

* OOP
* modularização forte
* baixo acoplamento
* separação clara de responsabilidades
* docstrings consistentes
* nomenclatura estável e previsível

## 8.2 Maintainability

A arquitetura deve permitir:

* adicionar novos coletores sem alterar o núcleo
* evoluir regras de normalização sem quebrar comparação
* trocar formato de saída com mínimo impacto

## 8.3 Testability

As regras centrais devem ser construídas de forma testável, especialmente:

* normalização
* matching
* cálculo de cenários

## 8.4 Determinism

O comportamento do MVP deve ser previsível e explicável, evitando heurísticas obscuras.

---

## 9. Proposed Architecture

## 9.1 High-Level Flow

Entrada:

1. lista de compras

Processamento:
2. coleta de ofertas
3. normalização de produtos
4. matching entre item e oferta
5. cálculo de cenários
6. geração da recomendação

Saída:
7. exibição em CLI e/ou JSON

---

## 9.2 Suggested Modules

```text
market_quote_assistant/
├── app/
│   ├── main.py
│   ├── domain/
│   ├── collectors/
│   ├── normalization/
│   ├── matching/
│   ├── comparison/
│   ├── services/
│   ├── output/
│   └── shared/
├── data/
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

---

## 10. Domain Model

## 10.1 ShoppingItem

Representa um item desejado na lista de compras.

Responsabilidades:

* armazenar nome base
* armazenar quantidade desejada
* armazenar unidade esperada
* representar intenção de compra

Atributos iniciais sugeridos:

* id
* display_name
* normalized_name
* requested_quantity
* requested_unit

---

## 10.2 ProductOffer

Representa uma oferta encontrada em um mercado.

Responsabilidades:

* armazenar os dados brutos e normalizados da oferta
* representar preço, unidade e disponibilidade

Atributos iniciais sugeridos:

* market_name
* original_name
* normalized_name
* price
* currency
* available
* url
* size_value
* size_unit
* brand
* raw_payload

---

## 10.3 MatchedOffer

Representa o vínculo entre um item da lista e uma oferta encontrada.

Responsabilidades:

* indicar se a oferta é compatível com o item
* indicar grau de confiança
* armazenar justificativa da decisão

Atributos iniciais sugeridos:

* shopping_item
* product_offer
* match_type
* confidence_score
* notes

---

## 10.4 MarketQuote

Representa o resultado consolidado de um mercado para uma determinada lista.

Responsabilidades:

* agrupar as melhores ofertas válidas de um mercado
* calcular subtotal
* informar itens faltantes
* armazenar frete, se existir

Atributos iniciais sugeridos:

* market_name
* selected_offers
* missing_items
* subtotal
* delivery_fee
* total_cost

---

## 10.5 ComparisonResult

Representa o resultado final da comparação.

Responsabilidades:

* armazenar cenários avaliados
* apontar recomendação final
* justificar a decisão

Atributos iniciais sugeridos:

* market_quotes
* best_single_market
* best_combined_option
* best_final_recommendation
* missing_items
* summary_notes

---

## 11. Core Business Rules

## 11.1 Equivalence Rules

Uma oferta só pode ser tratada como equivalente se:

* a categoria base for compatível
* a variação essencial não mudar o produto
* unidade e quantidade forem comparáveis

Exemplos:

* “Leite Integral 1L” vs “Leite UHT Integral 1L” → comparável
* “Leite Integral” vs “Leite Desnatado” → não comparável
* “Arroz 5kg” vs “Arroz 1kg” → comparável apenas com ajuste por quantidade
* “Banana kg” vs “Banana unidade” → não comparável automaticamente no MVP

---

## 11.2 Price Comparison Rules

O sistema deve comparar:

* preço absoluto quando os produtos forem equivalentes diretos
* preço proporcional quando houver ajuste confiável de unidade/quantidade

Quando não houver comparação segura, a oferta não deve ser priorizada.

---

## 11.3 Recommendation Rules

A recomendação final deve considerar:

1. cobertura da lista
2. custo final
3. frete
4. número de pedidos
5. confiabilidade do matching

No MVP, a prioridade recomendada é:

* primeiro: cobertura completa
* segundo: menor custo final
* terceiro: menor número de pedidos

---

## 12. Data Strategy for MVP

No MVP, os dados serão controlados e previsíveis.

### Fonte inicial:

* arquivos JSON locais por mercado

### Objetivo:

* validar o motor do sistema sem depender de scraping real

### Exemplo:

* `data/shopping_list.json`
* `data/market_a.json`
* `data/market_b.json`

---

## 13. Output Strategy

## 13.1 CLI Output

O sistema deve apresentar:

* lista de itens
* ofertas escolhidas por mercado
* subtotal
* frete
* total final
* recomendação final

## 13.2 JSON Output

O sistema deve poder exportar uma estrutura simples e organizada para consumo futuro.

---

## 14. Error Handling

O sistema deve tratar com clareza:

* item sem ofertas compatíveis
* produto com unidade não identificada
* mercado sem dados válidos
* dado incompleto no input
* comparação impossível por falta de normalização suficiente

Sempre que possível, o sistema deve falhar de forma explicável, não silenciosa.

---

## 15. MVP Success Criteria

O MVP será considerado validado se conseguir:

* receber uma pequena lista de compras
* comparar pelo menos 2 mercados mockados
* identificar equivalências simples com boa confiabilidade
* calcular cenário de melhor mercado único
* calcular cenário de melhor combinação
* gerar recomendação clara e útil

Se, ao final, a saída já ajudar na decisão de compra, a hipótese principal do projeto estará validada.

---

## 16. Technical Guidelines

Durante a implementação, seguiremos estas regras:

### 16.1 OOP Discipline

Cada classe deve ter responsabilidade clara e limitada.

### 16.2 No God Classes

Nenhuma classe deve concentrar coleta, normalização, matching e comparação ao mesmo tempo.

### 16.3 Explicit Naming

Nomes devem refletir exatamente o papel da classe, método ou arquivo.

### 16.4 Strong Docstrings

Métodos públicos, classes centrais e serviços devem ter docstrings úteis.

### 16.5 Incremental Commits

Cada etapa deve gerar commits pequenos, sem misturar múltiplas responsabilidades.

---

## 17. First Implementation Milestones

## Milestone 1 — Project Skeleton

Criar a estrutura base do projeto.

## Milestone 2 — Domain Models

Criar entidades centrais do domínio.

## Milestone 3 — Mock Collector

Criar carregamento de ofertas via JSON local.

## Milestone 4 — Normalization Layer

Criar regras iniciais de normalização textual e de unidade.

## Milestone 5 — Matching Engine

Criar lógica de equivalência entre item e oferta.

## Milestone 6 — Comparison Engine

Criar cálculo de cenários.

## Milestone 7 — CLI Output

Criar saída legível para uso local.

## Milestone 8 — JSON Export

Criar saída estruturada.

---

## 18. Risks

Riscos principais do projeto:

* matching falso positivo
* comparações inválidas entre unidades diferentes
* excesso de complexidade cedo demais
* acoplamento entre coleta e comparação
* tentar resolver scraping antes de validar o motor

---

## 19. Future Evolution

Após o MVP, o projeto poderá evoluir para:

* coletores reais
* cache de preços
* histórico de cotações
* API
* interface web
* listas recorrentes salvas
* regras mais sofisticadas de equivalência
* ranking personalizado por preferência do usuário

---

## 20. Final Statement

O Market Quote Assistant é, no MVP, um sistema de apoio à decisão de compra, baseado em coleta controlada, normalização simples e comparação explicável de ofertas entre mercados.

Seu objetivo inicial não é automatizar pedidos, mas provar que a recomendação gerada é útil o suficiente para economizar tempo, esforço e dinheiro.

---