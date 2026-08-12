# Documentação da IA — Kando / Talent Passport

## Escopo e autoria

A camada de IA do Kando foi concebida e desenvolvida por | Andreia [![GitHub](https://img.shields.io/badge/GitHub-Deialima-181717?style=flat&logo=github)](https://github.com/Deialima) |: prompts, contratos JSON, regras de negócio, validações e testes locais. O backend Django realiza sua integração ao produto, oferecendo persistência, endpoints, autenticação e orquestração.

Esta documentação descreve a camada de IA como uma área própria do produto; ela não é apenas um detalhe interno do backend.

## Objetivo

A IA transforma currículo, vaga e respostas do candidato em informações úteis para preparação profissional:

1. estrutura currículo e vaga;
2. identifica compatibilidade e lacunas;
3. gera perguntas técnicas personalizadas;
4. avalia respostas com feedback;
5. consolida desempenho;
6. produz perfil profissional, recomendações e trilha de estudo.

## Princípio central

> IA é usada para julgamento qualitativo; código é usado para cálculo e regras determinísticas.

### A IA é responsável por

- extração semântica de currículos e vagas;
- interpretação de requisitos;
- comparação qualitativa entre perfil e vaga;
- geração de perguntas;
- avaliação textual de respostas;
- síntese de perfil e recomendações.

### O código é responsável por

- médias e scores;
- faixas de senioridade e proficiência;
- agregação por skill;
- limiares e regras de desbloqueio;
- correspondências de nome controladas;
- persistência, autenticação e validação de propriedade.

## Módulos

| Módulo | Entrada | Saída principal |
|---|---|---|
| Normalização de currículo | texto/PDF do currículo | candidato, skills, experiências, formação e certificações |
| Normalização de vaga | texto/PDF da vaga | requisitos, tecnologias, senioridade, área e elegibilidade |
| Matching | currículo e vaga estruturados | score, skills compatíveis/faltantes, forças e melhorias |
| Geração de perguntas | currículo e vaga estruturados | desafio em blocos e perguntas conceituais |
| Avaliação de respostas | pergunta, critérios, senioridade e resposta | score, skills, evidências e feedback |
| Agregação | avaliações individuais | score geral e desempenho por skill |
| Perfil profissional | currículo, matching e avaliação | resumo, nível, competências e recomendações |
| Trilha de estudo | lacunas e desempenho | passos priorizados e recursos sugeridos |

## Regras de negócio importantes

### Currículo

- Experiência técnica e senioridade são calculadas em código a partir dos dados estruturados.
- A IA pode extrair experiências e skills, mas não deve ser fonte final de cálculo numérico.

### Matching

- Distinguir sinônimos reais de relação geral ↔ específica.
- Exemplo: SQL e PostgreSQL não são equivalentes absolutos. Uma vaga que pede SQL pode ser compatível com experiência em PostgreSQL; o inverso pode representar lacuna parcial.
- Requisitos de elegibilidade merecem prioridade máxima quando não atendidos.

### Perguntas

- O desafio é conceitual; não deve exigir código.
- Tecnologias existentes somente na vaga devem gerar perguntas de familiaridade/consciência, não perguntas profundas de arquitetura ou trade-offs.
- Perguntas devem ser vinculadas a skills avaliadas e identificadas de forma estável.

### Avaliação

- Resposta vazia recebe score zero sem chamada à IA.
- As avaliações individuais são consolidadas por skill em código.
- O resultado por skill deve ser reutilizado por dashboard e trilha, evitando médias duplicadas.

### Talent Passport

- `proficiency_level` é calculado em código usando o nível de confiança da skill do currículo.
- Correspondência entre a skill do perfil e a skill do currículo usa match exato, depois case-insensitive.
- Se não houver correspondência, existe fallback explícito com log e indicação de confiança; não deve haver fallback silencioso.

## Contratos JSON

As respostas são solicitadas como JSON estruturado. O projeto possui canonicalização de chaves e valores para normalizar formatos legados ou em português para o contrato interno em inglês.

Exemplos de campos canônicos:

```text
technical_skills
required_skills
matching_skills
missing_skills