# Kando — Talent Passport

> Plataforma de preparação para processos seletivos em tecnologia: o candidato sobe currículo e vaga, recebe um score de compatibilidade, faz um simulado técnico personalizado e sai com uma trilha de estudo personalizada e um perfil consolidado (Talent Passport).

## 🔗 Links rápidos

| | |
|---|---|
| 🎥 Demo / vídeo | [link] (Em construção)|
| 🌐 Produto no ar | [link do deploy(Em construção)] |
| 📋 Pesquisa de Mercado| [link do dashbord(Em construção)] |
| 📐 Doc de Frontend | [docs/frontend.md](Em construção) |
| ⚙️ Doc de Backend | [docs/backend.md](Em construção) |
| 🤖 Doc de IA  | [docs/ai.md](Em construção) |

## 🎯 O problema

Candidatos de tecnologia costumam chegar em processos seletivos sem saber
exatamente onde estão fracos em relação aos requisitos reais da vaga
específica que estão disputando. "Estudar tudo" não é viável no pouco tempo
que normalmente existe entre a candidatura e a entrevista.

## 💡 A solução

O candidato sobe o próprio currículo e a vaga desejada, ao mesmo tempo. A
plataforma extrai e estrutura os dois documentos com IA, Entrega um score de
compatibilidade e as lacunas de skill, gera um desafio técnico personalizado
pra esse par currículo-vaga, avalia as respostas por skills, e devolve um
plano de estudo priorizado pelas lacunas reais encontradas — tudo isso sem
nenhum recrutador alimentando a plataforma.



##  Funcionalidades

- [x] Análise automática de currículo
- [x] Análise automática de vaga
- [x] Score de compatibilidade currículo × vaga
- [x] Geração de desafio técnico personalizado (perguntas conceituais por skill)
- [x] Avaliação de resposta com IA, com feedback por skill
- [x] Dashboard de desempenho (por skill) — cálculo 100% em código, sem IA
- [ ] Trilha de estudo priorizada — lógica pronta e testada; endpoint ainda não exposto na API
- [ ] Talent Passport — perfil consolidado — lógica pronta e testada; endpoint ainda não exposto na API

##  Arquitetura

Visão geral do fluxo:

```
Currículo ──┐
            ├─→ Matching ─→ Desafio Técnico ─→ Avaliação de Respostas ─┐
Vaga ───────┘                                                          │
                                                                        ▼
                                        Dashboard ←── Trilha de Estudo ←┴─→ Talent Passport
```

Para detalhes de implementação de cada parte, veja as docs específicas linkadas acima.

##  Tecnologias

| Camada | Stack |
|---|---|
| **Frontend** | ![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![Vite](https://img.shields.io/badge/Vite_8-646CFF?style=for-the-badge&logo=vite&logoColor=white) ![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=reactrouter&logoColor=white) ![Mantine](https://img.shields.io/badge/Mantine-339AF0?style=for-the-badge&logo=mantine&logoColor=white) ![MUI](https://img.shields.io/badge/MUI-007FFF?style=for-the-badge&logo=mui&logoColor=white) ![Axios](https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white) ![jsPDF](https://img.shields.io/badge/jsPDF-E34F26?style=for-the-badge&logo=javascript&logoColor=white) |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django_6-092E20?style=for-the-badge&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/Django_REST_Framework-A30000?style=for-the-badge&logo=django&logoColor=white) |
| **Banco** | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white) |
| **IA** | ![Groq](https://img.shields.io/badge/Groq_API-F55036?style=for-the-badge&logo=groq&logoColor=white) ![Llama](https://img.shields.io/badge/Llama_3.3_70B-0467DF?style=for-the-badge&logo=meta&logoColor=white) ![JSON](https://img.shields.io/badge/JSON_Structured_Output-000000?style=for-the-badge&logo=json&logoColor=white) |
| **PDFs** | ![Docling](https://img.shields.io/badge/Docling-1A73E8?style=for-the-badge&logo=readthedocs&logoColor=white) |
| **Autenticação** | ![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white) |
| **Deploy** | ![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white) ![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white) ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white) |
| **Gestão de tarefas** | ![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white) |

##  Como rodar localmente

### Backend
```bash
cd backend
python -m venv .venv
# ative o venv conforme seu sistema operacional
pip install -r requirements.txt
```

Crie `backend/.env`:
```env
(Em construção)
```

```bash
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

> A API deve estar disponível em `Em construção`.
> Detalhes completos em [docs/frontend.md](Em construção), [docs/backend.md](Em construção) e [docs/ai.md](Em construção)

## 👥 Equipe

| Nome | Papel | GitHub |
|------|-------|--------|
| Nícolas | Frontend | [![GitHub](https://img.shields.io/badge/GitHub-NicolasSG-181717?style=flat&logo=github)](https://github.com/NicolasSG) |
| Karina | Backend | [![GitHub](https://img.shields.io/badge/GitHub-KarinaS0uza-181717?style=flat&logo=github)](https://github.com/KarinaS0uza) |
| Andreia | IA | [![GitHub](https://img.shields.io/badge/GitHub-Deialima-181717?style=flat&logo=github)](https://github.com/Deialima) |
## 📅 Status do projeto

Construído para o Hackathon Juninhos-Nortjobs, entre 16/07/2026 e 16/08/2026.

- [~] Núcleo de IA desenvolvido: normalização, matching, geração de perguntas,
  avaliação, dashboard, trilha e Talent Passport
- [~] Testes locais dos contratos JSON, prompts, regras determinísticas e
  integrações entre módulos de IA
- [~] Implementação e integração dos módulos pelo backend em andamento
- [~] Frontend funcional — algumas telas ainda utilizam dados simulados
- [~] Validação completa do fluxo contra a API real do Groq
- [~] Deploy em produção

