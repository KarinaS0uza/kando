"""PDF text extraction service using pdfplumber."""

# Mirrors resumes/services/pdf_extraction.py by design, since both apps run
# the identical pdfplumber pipeline; suppress the cross-file duplicate-code
# report until that flow is extracted.
# pylint: disable=duplicate-code

import logging

import pdfplumber
from pdfminer.pdfdocument import PDFEncryptionError, PDFPasswordIncorrect
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.psparser import PSSyntaxError

from .storage import get_temp_pdf_path, temp_storage

logger = logging.getLogger(__name__)

PDF_PARSE_ERRORS = (PDFSyntaxError, PSSyntaxError, PDFPasswordIncorrect, PDFEncryptionError)


class PdfExtractionError(Exception):
    """Raised when no usable text can be extracted from a PDF."""


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from an uploaded PDF file.

    Args:
        pdf_file (django.core.files.uploadedfile.UploadedFile): PDF file
            uploaded through the API request.

    Returns:
        The extracted text, one page per paragraph.

    Raises:
        PdfExtractionError: When the temp file cannot be saved, the PDF
            cannot be parsed, or no usable text can be extracted.
    """
    try:
        name, path = get_temp_pdf_path(pdf_file)
    except OSError as exc:
        raise PdfExtractionError(
            "Não foi possível salvar o PDF para processamento. Tente novamente mais tarde."
        ) from exc
    try:
        try:
            with pdfplumber.open(path) as pdf:
                text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
        except PDF_PARSE_ERRORS as exc:
            raise PdfExtractionError(
                "Não foi possível processar o PDF. Verifique se o arquivo não está "
                "corrompido ou protegido por senha."
            ) from exc
    finally:
        try:
            temp_storage.delete(name)
        except OSError:
            logger.warning("pdf_extraction: failed to delete temp file %s", name, exc_info=True)

    if not text or not text.strip():
        raise PdfExtractionError("Não foi possível extrair texto utilizável do PDF.")

    return text
