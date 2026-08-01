# jobs/services/job_llm_normalization.py
"""LLM-based normalization of job posting text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
JobPosting is persisted. Requires GROQ_API_KEY in the environment.
"""

import json
import os

from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


PROMPT_TEMPLATE = """Você é um especialista em análise de vagas de emprego. O texto abaixo foi
copiado de um site de vagas (como Indeed, LinkedIn, etc.) e PODE conter
elementos irrelevantes misturados, como: menu de navegação, botões
("Candidatar-se", "Salvar vaga", "Compartilhar"), vagas similares/sugeridas,
avaliações da empresa, ou texto duplicado.

Ignore completamente esses elementos e extraia informação APENAS do conteúdo
real da descrição da vaga (requisitos, responsabilidades, benefícios, etc.).

Se o texto estiver desorganizado, sem quebras de linha claras, ou fora de
ordem, reorganize mentalmente antes de extrair os dados.

Retorne APENAS um JSON válido, sem texto adicional, sem markdown, seguindo
EXATAMENTE esta estrutura e esta regra:

- "requisitos_elegibilidade" deve conter APENAS requisitos de elegibilidade legal/administrativa que não são skills técnicas — exemplos: cidadania exigida, clearance de segurança, vistos de trabalho obrigatórios, licenças ou registros profissionais obrigatórios por lei (ex: CRM, OAB, CREA). NÃO inclua aqui requisitos técnicos comuns (linguagens, frameworks, anos de experiência) — esses continuam em "requisitos_obrigatorios". Se a vaga não mencionar nenhum requisito desse tipo, retorne uma lista vazia []

{{
  "vaga": {{"titulo": string, "empresa": string, "localizacao": string, "modelo_trabalho": "presencial" | "remoto" | "hibrido"}},
  "requisitos_obrigatorios": [string],
  "requisitos_desejaveis": [string],
  "requisitos_elegibilidade": [string],
  "responsabilidades": [string],
  "tecnologias_mencionadas": [{{"nome": string, "categoria": "linguagem" | "framework" | "ferramenta" | "banco_de_dados" | "cloud" | "metodologia_ou_conceito" | "outro"}}],
  "senioridade_esperada": "junior" | "pleno" | "senior" | "especialista",
  "area_vaga": string,
  "metadata": {{"confianca_geral_analise": number, "campos_nao_encontrados": [string]}}
}}

Exemplos de referência para categorizar tecnologias corretamente (evite confundir):
- "linguagem": HTML, HTML5, CSS, CSS3, JavaScript, TypeScript, Python, Java, R
- "framework": React, Angular, Vue.js, Express, Django, Next.js
- "ferramenta": Git, Jest, Cypress, Selenium, Playwright, Kubernetes, Docker, D3.js, ECharts, Plotly
- "cloud": AWS, Azure, Azure Government, Google Cloud Platform, GCP
- "banco_de_dados": PostgreSQL, MongoDB, MySQL, Redis
- "metodologia_ou_conceito": Machine Learning, Deep Learning, Agile, DevOps, Scrum, Design Patterns

Vaga:
{vaga}
"""


def _call_llm(text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(vaga=text)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def normalize_job_posting(text: str) -> dict:
    """
    Returns the structured JSON from the LLM on success, or
    {"error": str, "retryable": bool} on failure.
    """
    if not text or not text.strip():
        return {"error": "Empty job posting text", "retryable": False}
    try:
        return _call_llm(text)
    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON", "retryable": True}
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Service boundary: any failure calling the LLM must degrade to
        # {"error": ...} instead of propagating, so JobPosting creation
        # never breaks because the LLM call failed.
        return {"error": f"Failed to call the LLM: {exc}", "retryable": True}
