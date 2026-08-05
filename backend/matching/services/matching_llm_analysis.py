"""LLM-based compatibility analysis between a resume and a job posting.

Runs on demand, after both the ResumeSubmission and the JobPostingSubmission
have a successful normalization. Requires GROQ_API_KEY in the environment.
"""

import json
import os
import time
from string import Template

from groq import Groq

from ai_core.models import Prompt, PromptCallMetadata

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

PROMPT_KEY = "job_resume_matching_analysis"

# The LLM service modules share the same call/logging boilerplate by design.
# pylint: disable=duplicate-code


def _call_llm(resume_structured_data: dict, job_structured_data: dict) -> dict:
    prompt_row = None
    formatted_prompt = ""
    output_text = None
    error_message = None
    usage = None
    status = PromptCallMetadata.Status.API_ERROR
    started_at = time.monotonic()
    try:
        prompt_row = Prompt.objects.get(prompt_description=PROMPT_KEY, is_active=True)
        formatted_prompt = Template(prompt_row.prompt_detail).safe_substitute(
            resume=json.dumps(resume_structured_data, ensure_ascii=False),
            vaga=json.dumps(job_structured_data, ensure_ascii=False),
        )
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        usage = response.usage
        output_text = response.choices[0].message.content
        output_data = json.loads(output_text)
        status = PromptCallMetadata.Status.SUCCESS
        return output_data
    except Prompt.DoesNotExist as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.PROMPT_MISSING
        raise
    except json.JSONDecodeError as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.INVALID_JSON
        raise
    except Exception as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.API_ERROR
        raise
    finally:
        PromptCallMetadata.objects.create(
            prompt=prompt_row,
            prompt_description=prompt_row.prompt_description if prompt_row else PROMPT_KEY,
            version=prompt_row.version if prompt_row else None,
            model_name=MODEL,
            status=status,
            input_text=formatted_prompt,
            output_text=output_text,
            error_message=error_message,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            duration_ms=int((time.monotonic() - started_at) * 1000),
        )


def analyze_match(resume_structured_data: dict, job_structured_data: dict) -> dict:
    """
    Returns the structured JSON from the LLM on success, or
    {"error": str, "retryable": bool} on failure.
    """
    try:
        return _call_llm(resume_structured_data, job_structured_data)
    except Prompt.DoesNotExist:
        return {"error": "Prompt de matching não configurado", "retryable": False}
    except json.JSONDecodeError:
        return {"error": "O LLM retornou um JSON inválido", "retryable": True}
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Service boundary: any failure calling the LLM must degrade to
        # {"error": ...} instead of propagating, so MatchResult creation
        # never breaks because the LLM call failed.
        return {"error": f"Falha ao chamar o LLM: {exc}", "retryable": True}
