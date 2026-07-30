# jobs/services/pdf_extraction.py
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from .storage import get_temp_pdf_path, temp_storage


class PdfExtractionError(Exception):
    """Raised when no usable text can be extracted from a PDF."""


def extract_text_from_pdf(pdf_file) -> str:
    name, path = get_temp_pdf_path(pdf_file)
    print(path, "CHEGOU AQUI")
    try:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        result = converter.convert(path)
        markdown = result.document.export_to_markdown()
    finally:
        temp_storage.delete(name)

    if not markdown or not markdown.strip():
        raise PdfExtractionError("No usable text could be extracted from the PDF.")

    return markdown