# Documentação do Backend — Kando

## Escopo e autoria

A camada de Backend do Kando foi concebida e desenvolvida por | Karina [![GitHub](https://img.shields.io/badge/GitHub-KarinaS0uza-181717?style=flat&logo=github)](https://github.com/KarinaS0uza) |

## Visão geral

O backend do Kando é uma API Django REST responsável por autenticação, persistência, processamento de currículos e vagas, orquestração dos módulos de IA, matching, avaliação técnica, dashboard, trilha e Talent Passport.

## Stack

- Python e Django 6
- Django REST Framework
- JWT (`djangorestframework-simplejwt`)
- Docling para extração de texto de PDFs
- Groq para chamadas ao modelo de IA
- SQLite para desenvolvimento local
- PostgreSQL/Supabase opcional para banco remoto

## Apps

| App | Responsabilidade |
|---|---|
| `users` | usuário customizado, cadastro, login e CRUD |
| `resumes` | envio, extração e normalização de currículos |
| `jobs` | envio, extração e normalização de vagas |
| `matching` | comparação entre currículo e vaga |
| `assessments` | geração, respostas e avaliação do simulado |
| `passports` | dashboard, trilha, Passport e autoavaliação |
| `ai_core` | prompts, chamadas à IA, metadados e contratos JSON |
| `config` | configurações e roteamento global |

## Autenticação

O backend usa JWT. Salvo cadastro e login, as rotas exigem autenticação.

```http
Authorization: Bearer <access_token>
```

Rotas públicas:

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/users/create/` | Cadastro |
| `POST` | `/api/login/` | Retorna access token, refresh token e `user_id` |

## Endpoints

### Usuários

| Método | Rota |
|---|---|
| `GET` | `/api/users/` |
| `GET` | `/api/users/<uuid>/` |
| `PUT/PATCH` | `/api/users/<uuid>/update/` |
| `DELETE` | `/api/users/<uuid>/delete/` |

### Currículos e vagas

| Método | Rota | Corpo principal |
|---|---|---|
| `GET, POST` | `/api/resumes/` | texto bruto ou PDF |
| `GET` | `/api/resumes/<uuid>/` | — |
| `GET, POST` | `/api/job-postings/` | texto bruto ou PDF |
| `GET` | `/api/job-postings/<uuid>/` | — |

As submissões são normalizadas. Em caso de falha da IA, o backend registra o estado de erro sem derrubar toda a aplicação.

### Matching

| Método | Rota | Corpo |
|---|---|---|
| `GET, POST` | `/api/matching/` | `{ "resume_id": "...", "job_id": "..." }` |
| `GET` | `/api/matching/<uuid>/` | — |

O resultado inclui score geral, `matches`, `gaps`, forças e pontos de melhoria.

### Simulado

| Método | Rota | Corpo |
|---|---|---|
| `GET, POST` | `/api/assessments/` | `{ "resume_id": "...", "job_id": "..." }` |
| `GET, DELETE` | `/api/assessments/<uuid>/` | — |
| `POST` | `/api/assessments/<uuid>/result/` | `{ "answers": [{ "id": "B1Q1", "answer": "..." }] }` |

O resultado do simulado contém avaliação por pergunta, score agregado e dados por skill.

### Talent Passport

| Método | Rota | Corpo |
|---|---|---|
| `GET, POST` | `/api/passports/` | `{ "resume_id": "...", "job_id": "..." }` |
| `GET` | `/api/passports/<uuid>/` | — |
| `GET, POST` | `/api/passports/waiting-readiness/` | autoavaliação de preparo |

Pré-requisitos para gerar um Passport: currículo e vaga normalizados, matching concluído, simulado gerado e respostas corrigidas. Um Passport é único por par currículo/vaga; gerar novamente atualiza o existente.

## Fluxo de dados