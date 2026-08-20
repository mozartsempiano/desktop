# Diretrizes Operacionais do AGENTS.md

## Diretriz Principal

- Evite trabalhar em mais de um arquivo por vez.
- Múltiplas edições simultâneas em um arquivo causarão corrupção.
- Ensine sobre o que você está fazendo enquanto programa, mas não enrole desnecessariamente. Seja direto e sussinto.
- Sempre adicione o número da linha e o nome do arquivo ao fazer referência a código.

## Protocolo para arquivos grandes e alterações complexas

### Fase de planejamento obrigatória

Ao trabalhar com arquivos grandes (>300 linhas) ou alterações complexas:

1. SEMPRE comece criando um plano detalhado ANTES de fazer qualquer edição.
2. Seu plano DEVE incluir:

- Todas as funções/seções que precisam ser modificadas
- A ordem em que as alterações devem ser aplicadas
- Dependências entre as alterações
- Número estimado de edições separadas necessárias

3. Formate seu plano como:

```
## Plano de edição proposto

Trabalhando com: [nome do arquivo]
Total de edições planejadas: [número]
```

### Realizando edições

- Concentre-se em uma alteração conceitual por vez
- Mostre trechos claros de "antes" e "depois" ao propor alterações, deixando claro o que foi removido, o que foi adicionado, entre outros
- Inclua explicações concisas sobre o que mudou e por quê
- Sempre verifique se a edição mantém o estilo de código do projeto

### Sequência de edição:

1. [Primeira alteração específica] - Objetivo: [por quê]
2. [Segunda alteração específica] - Objetivo: [por quê]
3. Você aprova este plano? Prosseguirei com a Edição [número] após sua confirmação.
4. AGUARDE a confirmação explícita do usuário antes de fazer QUALQUER edição quando o usuário aprovar a edição [número]
5. Se você descobrir alterações adicionais necessárias durante a edição:
   - PARE e atualize o plano
   - Obtenha aprovação antes de continuar

### Prevenção de limites de taxa

- Para arquivos muito grandes, sugira dividir as alterações entre várias sessões
- Priorize alterações que formem unidades logicamente completas
- Sempre forneça pontos claros de parada

## Requisitos Gerais

Use tecnologias modernas, conforme descrito abaixo, para todas as sugestões de código. Priorize código limpo e de fácil manutenção futura, sem comentários desnecessários ou redundantes. Quando possível, as soluções devem ser simples e diretas, sem inventar moda ou fazer nada que não seja estritamente necessário para o funcionamento do que foi pedido pelo usuário. Sempre busque reutilizar funções, classes e código já existente, em vez de criar novos, a fim de evitar bloat. Organize adequadamente os arquivos, mantendo o estilo atual do projeto.

Priorize usar HTML, CSS e Nunjucks, usando JavaScript apenas quando for estritamente necessário, normalmente para lógica de código, de fato.

Não adicione uma infinidade de fallbacks e aliases, porque isso pode poluir o projeto. Apenas faça o projeto funcionar de uma forma uniformizada e lógica. Apague trechos não-utilizados.

### Acessibilidade

- Garanta conformidade com o nível AA da **WCAG 2.1**, no mínimo, e AAA sempre que viável.
- Sempre sugira:
  - Rótulos para campos de formulário.
  - Funções e atributos **ARIA** adequados.
  - Contraste de cores adequado.
  - os alternativos (`alt`, `aria-label`) para elementos de mídia.
  - HTML semântico para uma estrutura clara.

## Compatibilidade com Navegadores

- Priorize a detecção de recursos (`if ('fetch' in window)`, etc.).
- Ofereça suporte
