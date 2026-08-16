# Documentação do Frontend — Kando

## Escopo e autoria

A camada de Frontend do Kando foi concebida e desenvolvida por  Nícolas [![GitHub](https://img.shields.io/badge/GitHub-NicolasSG-181717?style=flat&logo=github)](https://github.com/NicolasSG) 

## Visão geral

O frontend do Kando é uma aplicação React que conduz a pessoa candidata pelo fluxo de envio de currículo e vaga, análise de compatibilidade, simulado, dashboard, trilha de estudo e Talent Passport.

## Stack

- React 19 (19.2.7) e Vite (8.1.1) — SPA pura, sem Next.js
- React Router (`react-router-dom`, v7.18.1)
- Axios para comunicação com a API
- Mantine (`@mantine/core`) e Material UI (`@mui/material`) para componentes
- `devicon`, `lucide-react` e `@phosphor-icons` para ícones; `react-hot-toast` para notificações
- jsPDF para exportar o certificado
- Canvas/compositor de imagens para o Talent Passport
- `react-pdf` e `react-dropzone` para upload e visualização de PDF
- `react-archer` e `@react-spring/web` para elementos visuais/animações (ex.: trilha de estudo)

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

> **Divergência conhecida:** `routes/routeConfig.js` lista uma rota `/report` que **não
> existe** em `AppRoutes.jsx` (ver seção "Rotas" abaixo). Pode ser uma rota planejada e nunca
> implementada, ou removida sem atualizar essa lista de config — vale confirmar com o time
> antes de tratar `routeConfig.js` como fonte de verdade das rotas.

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

> **Onde isso acontece no código:** a gravação ocorre em
> `components/layout/JoinForm.jsx`; a leitura, em `hooks/useAuth.js` (usado pelo
> `ProtectedRoute`) e nos interceptors Axios dos três services listados abaixo; a remoção
> acontece em `components/layout/Header.jsx` (logout) e também ao montar `pages/Login.jsx`.
> Não há cookie nem Context API/provider de auth dedicado — é `localStorage` puro.

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

> **Débito técnico conhecido:** cada um desses três arquivos cria sua própria instância
> `axios.create()` e seu próprio interceptor, em vez de compartilhar uma configuração única
> — duplicação já assinalada em comentário no próprio código-fonte.

Principais services:

| Arquivo | Responsabilidade |
|---|---|
| `services/api.js` | cadastro, login, usuários, currículos, vagas e matching |
| `services/simulationService.js` | criação, consulta e envio das respostas do simulado |
| `services/talentPassportService.js` | Passport, dashboard, trilha e autoavaliação |
| `services/passportService.js` | adaptação dos dados para o certificado visual |
| `services/imageComposer/` | composição do certificado em canvas |
| `utils/uploadTracker.js` | coordenação das requisições assíncronas de upload, matching e simulado |

> **Nota:** nenhum mock ou dado hardcoded foi encontrado substituindo chamada real de API —
> todas as telas com dados consomem a API de fato. Os únicos arquivos "falsos" no projeto são
> stubs vazios **sem consumidores** (não são mocks ativos em uso hoje):
> `services/githubService.js` e `services/resumeService.js` (ambos com comentário explícito
> "not implemented"), e os hooks `hooks/useProfileAnalysis.js` e `hooks/useSimulation.js`
> (placeholders retornando `{}`, também sem uso real em nenhuma tela).

### Fluxo integrado

1. A pessoa candidata envia currículo e vaga.
2. O frontend cria o matching e encaminha para a tela de score.
3. O simulado é carregado com perguntas geradas pelo backend.
4. As respostas são enviadas para correção; é possível pular uma pergunta, que é enviada como resposta vazia.
5. Dashboard, trilha e Passport usam os dados reais da API.

## Score e simulado

A tela de score exibe skills compatíveis e lacunas. Quando há muitas skills, mostra as seis primeiras e oferece **"Ver mais"**.

No simulado:

- perguntas usam o campo `prompt` da API;
- respostas usam o campo `answer`;

## Débitos técnicos conhecidos

Não há marcadores formais `TODO`/`FIXME` no frontend, mas há trabalho incompleto sinalizado
diretamente no código:

- Stubs/placeholders sem uso real (`githubService.js`, `resumeService.js`,
  `useProfileAnalysis.js`, `useSimulation.js` — ver seção "Integração com a API").
- Duplicação de `axios.create()`/interceptor entre `api.js`, `simulationService.js` e
  `talentPassportService.js`.
- Um `console.error` de debug esquecido em `hooks/useImageComposer.js` (linha 33).
- Um "Caveat" documentado em `utils/uploadTracker.js`: o rastreamento de promises usa um
  **slot único** (não é por usuário/aba), e é **sobrescrito silenciosamente** caso um novo
  ciclo de upload/matching/simulado comece antes do anterior terminar — vale atenção em
  cenários de múltiplas abas ou uploads concorrentes.
- A divergência entre `routes/routeConfig.js` e `AppRoutes.jsx` (rota `/report`), já
  sinalizada na seção "Estrutura principal".
