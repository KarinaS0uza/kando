# Talent Passport (KANdo) — Frontend

Plataforma de "job readiness": o candidato envia seu currículo e a vaga que
deseja, recebe uma análise de compatibilidade (% de match, habilidades que
já tem vs. habilidades que faltam), passa por uma simulação de entrevista
técnica gerada a partir desse par currículo/vaga, e ao final desbloqueia o
**Talent Passport** — um certificado visual com "carimbos" de competências
validadas pelo desempenho real na simulação, não apenas pelo que o
currículo alega.

Este README cobre só o frontend (`frontend/`). O backend (Django REST
Framework) vive em `../backend` e tem sua própria configuração.

## Stack técnica

- **Vite 8 + React 19 + React Router 7** — SPA client-side, sem SSR.
- **CSS puro**, sem Tailwind nem CSS-in-JS de time. Cada página/componente
  tem seu próprio arquivo `.css` importado diretamente (ex.:
  `Dashboard.jsx` importa `Dashboard.css`). A única exceção é
  `Slider.jsx`, que usa CSS Modules (`Slider.module.css`) porque envolve
  os subcomponentes internos do `@base-ui/react/slider` — isolamento por
  build evita colisão de nome com as classes desses subcomponentes.
- **MUI (`@mui/material`) usado seletivamente**, não como base do design
  system: `CircularProgress` (loading spinner, gauge de compatibilidade),
  `Popover`/`Modal`/`Backdrop` (dicas contextuais, os 3 modais de
  onboarding). O resto da interface é CSS próprio — MUI entra só onde um
  componente pronto (com acessibilidade e animação já resolvidas) economiza
  trabalho sem impor um visual genérico ao resto do app.
- **Mantine (`@mantine/core`)** — usado pontualmente (`Timeline` na trilha
  de estudo, `MantineProvider` envolvendo o app inteiro em `App.jsx`).
- **`react-hot-toast`** para notificações de erro/sucesso (uploads,
  falhas de rede).
- **`@react-spring/web`** para a transição customizada (`Fade`) usada nos
  3 modais.
- **`react-dropzone` + `react-pdf`** para o upload de currículo/vaga em PDF
  com preview inline.
- **`devicon`** para os ícones de tecnologia estampados no certificado.
- **`oxlint`** como linter (não ESLint) — `npm run lint`.

Por que CSS puro em vez de Tailwind: o projeto optou por arquivos CSS
dedicados por componente/página em vez de classes utilitárias inline. Isso
mantém o JSX mais legível quando o layout é complexo (ex.: o certificado
canvas, o gauge de compatibilidade com SVG customizado) e evita a curva de
aprendizado extra de Tailwind para quem só mexe na lógica.

## Como rodar localmente

```bash
cd frontend
npm install
npm run dev       # abre automaticamente em http://localhost:5173 (ou a porta livre seguinte)
```

Outros comandos:

```bash
npm run build      # build de produção (Vite)
npm run preview    # serve o build de produção localmente
npm run lint        # oxlint
```

### Variáveis de ambiente

Copie `.env.example` para `.env`:

```bash
VITE_API_URL=http://localhost:8000
```

**Atenção:** hoje essa variável não é lida em nenhum lugar do código — os
3 clientes Axios do projeto (`src/services/api.js`,
`simulationService.js`, `talentPassportService.js`) usam
`http://localhost:8000/api` **hardcoded** na criação do `axios.create()`,
em vez de `import.meta.env.VITE_API_URL`. Ou seja, mudar `.env` não muda
para onde o frontend aponta — para rodar contra um backend em outro host,
hoje é preciso editar essas 3 URLs diretamente no código.

O backend precisa estar rodando (por padrão em `http://localhost:8000`)
para qualquer fluxo autenticado funcionar — não há mock de API no
frontend para o fluxo real de login/signup (só o login com Google é mock,
ver seção de componentes).

## Estrutura de pastas

```
src/
├── assets/          # imagens, SVGs, PNGs dos carimbos do certificado
├── components/
│   ├── layout/       # componentes com identidade própria de bloco: Header,
│   │                  # modais, formulário de login/signup, upload, certificado
│   └── ui/           # componentes menores/genéricos: loading, popover
├── hooks/            # useAuth, useImageComposer + 2 stubs não implementados
├── pages/            # uma página por rota (ver seção de rotas abaixo)
├── routes/           # AppRoutes.jsx (fonte de verdade das rotas)
├── services/         # clientes de API + agregadores de dados (view-models)
└── utils/            # funções puras de transformação de dados + o
                       # coordenador de uploads/match/simulado em voo
```

`src/routes/routeConfig.js` existe mas é código morto — não é importado em
lugar nenhum e está desatualizado em relação às rotas reais (`AppRoutes.jsx`
é a fonte de verdade).

## Rotas e fluxo principal

Todas as rotas autenticadas passam por `ProtectedRoute` (redireciona para
`/login` se não houver sessão).

| Rota | Página | Acesso |
|---|---|---|
| `/` | `HomePage` | público |
| `/login` | `Login` | público |
| `/signup` | `Signup` | público |
| `/upload` | `UploadProfile` | autenticado |
| `/upload/reliability` | `Reliability` | autenticado |
| `/score` | `Score` | autenticado |
| `/simulation/instructions` | `SimulationInstructions` | autenticado |
| `/simulation/questions` | `SimulationQuestions` | autenticado |
| `/dashboard` | `Dashboard` | autenticado |
| `/study-path` | `StudyPath` | autenticado |
| `/talent-passport` | `TalentPassport` | autenticado |

Fluxo principal (candidato novo, do cadastro ao resultado):

1. **`/` → `/login` ou `/signup`** — `JoinForm` (email/senha, real, via
   `services/api.js`) ou o botão do Google (mock, ver
   `components/layout/GoogleButton.jsx`).
2. **`/upload`** — o candidato envia currículo + descrição da vaga (PDF ou
   texto colado). Ao submeter, `UploadProfile` dispara as duas requisições
   de criação (`createResume`/`createJobPosting`) **sem aguardar** e já
   navega para a próxima tela, guardando as promises em
   `utils/uploadTracker.js` para a tela seguinte recuperar.
3. **`/upload/reliability`** — enquanto aguarda os uploads concluírem
   (`waitForUploads`), o candidato responde duas perguntas de
   autopercepção (o quão preparado se sente, qual % de match considera
   suficiente pra se candidatar). Ao confirmar, dispara em paralelo o
   cálculo do match e a geração das perguntas da simulação
   (`startMatch`/`startQuestions`, também sem aguardar) e navega para
   `/score`.
4. **`/score`** — tela de matching: % de compatibilidade em um gauge
   circular, lista de "Habilidades compatíveis" vs. "Habilidades
   faltantes" conectadas ao gauge por linhas guia.
5. **`/simulation/instructions` → `/simulation/questions`** — teste
   técnico gerado com base no par currículo/vaga.
6. **`/dashboard`, `/study-path`, `/talent-passport`** — telas de
   resultado: painel geral de desempenho, trilha de estudo personalizada
   baseada nos gaps, e o certificado Talent Passport com os carimbos de
   competência (bloqueados/desbloqueados conforme o desempenho na
   simulação — ver `components/layout/PassportCertificate.jsx`).

O `Header` (nav global) só mostra o menu completo depois que o candidato
já tem um match calculado (`hasCompletedMatch`), e intercepta o link do
Simulado com um modal de aviso (`SimulationGateModal`) se ele já tiver
concluído um simulado antes — para refazer, precisa passar por uma nova
comparação currículo/vaga.

## Documentação em código

Componentes reutilizáveis (`components/layout/`, `components/ui/`) têm um
bloco de comentário no topo do arquivo com propósito, props esperadas e
qualquer decisão não óbvia. Funções utilitárias, hooks e services têm
JSDoc. Comentários focam no "porquê" (regras de negócio, workarounds,
contratos implícitos com o backend) — não descrevem o óbvio linha a linha.
Uma lista de itens que ficaram com documentação só factual, por
dependerem de contexto de negócio que não está disponível no código, está
no final da entrega desta documentação (ver histórico de conversa/PR).
