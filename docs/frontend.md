# Documentação do Frontend — Kando

## Escopo e autoria

A camada de Frontend do Kando foi concebida e desenvolvida por  Nícolas [![GitHub](https://img.shields.io/badge/GitHub-NicolasSG-181717?style=flat&logo=github)](https://github.com/NicolasSG) 

## Visão geral

O frontend do Kando é uma aplicação React que conduz a pessoa candidata pelo fluxo de envio de currículo e vaga, análise de compatibilidade, simulado, dashboard, trilha de estudo e Talent Passport.

## Stack

- React 19 e Vite
- React Router
- Axios para comunicação com a API
- Mantine e Material UI para componentes
- jsPDF para exportar o certificado
- Canvas/compositor de imagens para o Talent Passport

## Estrutura principal

```text
frontend/src/
  pages/        # telas da aplicação
  components/   # componentes reutilizáveis e layout
  services/     # chamadas à API e composição de imagem
  hooks/        # estado e lógica reutilizável
  routes/       # rotas públicas e autenticadas
  utils/        # utilitários do fluxo
```

## Rotas

| Rota | Tela | Finalidade |
|---|---|---|
| `/` | HomePage | Página inicial |
| `/login` | Login | Autenticação |
| `/signup` | Signup | Criação de conta |
| `/upload` | UploadProfile | Envio de currículo e vaga |
| `/upload/reliability` | Reliability | Autoavaliação de preparo |
| `/score` | Score | Resultado do matching |
| `/simulation/instructions` | SimulationInstructions | Instruções do simulado |
| `/simulation/questions` | SimulationQuestions | Perguntas e respostas |
| `/dashboard` | Dashboard | Desempenho e recomendações |
| `/study-path` | StudyPath | Trilha de estudo |
| `/talent-passport` | TalentPassport | Certificado e compartilhamento |

As rotas de produto usam `ProtectedRoute` e exigem sessão ativa.

## Autenticação e sessão

Após login ou cadastro, o frontend armazena:

```text
localStorage.token   # access token JWT
localStorage.user_id # UUID do usuário
```

O token é enviado no header:

```text
Authorization: Bearer <token>
```

No logout, token, `user_id` e estados locais relacionados ao fluxo são removidos.

## Integração com a API

A URL-base da API é configurada por variável de ambiente:

```env
VITE_API_URL=http://localhost:8000/api
```

Os clientes Axios em `services/api.js`, `services/simulationService.js` e
`services/talentPassportService.js` usam `import.meta.env.VITE_API_URL` e
enviam automaticamente o JWT quando disponível.

```http
Authorization: Bearer <access_token>
```

Principais services:

| Arquivo | Responsabilidade |
|---|---|
| `services/api.js` | cadastro, login, usuários, currículos, vagas e matching |
| `services/simulationService.js` | criação, consulta e envio das respostas do simulado |
| `services/talentPassportService.js` | Passport, dashboard, trilha e autoavaliação |
| `services/passportService.js` | adaptação dos dados para o certificado visual |
| `services/imageComposer/` | composição do certificado em canvas |
| `utils/uploadTracker.js` | coordenação das requisições assíncronas de upload, matching e simulado |

### Fluxo integrado

1. A pessoa candidata envia currículo e vaga.
2. O frontend cria o matching e encaminha para a tela de score.
3. O simulado é carregado com perguntas geradas pelo backend.
4. As respostas são enviadas para correção; é possível pular uma pergunta, que é enviada como resposta vazia.
5. Dashboard, trilha e Passport usam os dados reais da API.

## Score e simulado

A tela de score exibe skills compatíveis e lacunas. Quando há muitas skills, mostra as seis primeiras e oferece **“Ver mais”**.

No simulado:

- perguntas usam o campo `prompt` da API;
- respostas usam o campo `answer`;
