"""PDF text extraction service using docling."""
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.serializer.markdown import (
    MarkdownDocSerializer,
    MarkdownParams,
)

from .storage import get_temp_pdf_path, temp_storage


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
        PdfExtractionError: When no usable text can be extracted.
    """
    name, path = get_temp_pdf_path(pdf_file)
    try:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        result = converter.convert(path)
        serializer = MarkdownDocSerializer(
            doc=result.document,
            params=MarkdownParams(image_placeholder="", include_hyperlinks=False),
        )
        markdown = serializer.serialize().text
    finally:
        temp_storage.delete(name)

    if not markdown or not markdown.strip():
        raise PdfExtractionError("Não foi possível extrair texto utilizável do PDF.")

    return markdown
