"""PDF text extraction service using docling."""

# Mirrors resumes/services/pdf_extraction.py by design, since both apps run
# the identical docling pipeline; suppress the cross-file duplicate-code
# report until that flow is extracted.
# pylint: disable=duplicate-code

import logging

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.exceptions import ConversionError
from docling_core.transforms.serializer.markdown import (
    MarkdownDocSerializer,
    MarkdownParams,
)

from .storage import get_temp_pdf_path, temp_storage

logger = logging.getLogger(__name__)


class PdfExtractionError(Exception):
    """Raised when no usable text can be extracted from a PDF."""


def extract_text_from_pdf(pdf_file) -> str:
    """Extract markdown text from an uploaded PDF file.

    Args:
        pdf_file (django.core.files.uploadedfile.UploadedFile): PDF file
            uploaded through the API request.

    Returns:
        The extracted text as markdown.

    Raises:
        PdfExtractionError: When the temp file cannot be saved, the PDF
            cannot be converted, or no usable text can be extracted.
    """
    try:
        name, path = get_temp_pdf_path(pdf_file)
    except OSError as exc:
        raise PdfExtractionError(
            "Não foi possível salvar o PDF para processamento. Tente novamente mais tarde."
        ) from exc
    try:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        try:
            result = converter.convert(path)
        except ConversionError as exc:
            raise PdfExtractionError(
                "Não foi possível processar o PDF. Verifique se o arquivo não está "
                "corrompido ou protegido por senha."
            ) from exc
        serializer = MarkdownDocSerializer(
            doc=result.document,
            params=MarkdownParams(image_placeholder="", include_hyperlinks=False),
        )
        markdown = serializer.serialize().text
    finally:
        try:
            temp_storage.delete(name)
        except OSError:
            logger.warning("pdf_extraction: failed to delete temp file %s", name, exc_info=True)

    if not markdown or not markdown.strip():
        raise PdfExtractionError("Não foi possível extrair texto utilizável do PDF.")

    return markdown
