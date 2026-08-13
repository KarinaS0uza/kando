"""Unit tests for resumes.services.pdf_extraction: parsing and I/O failure paths."""

# Mirrors jobs/test_pdf_extraction.py by design, since it exercises the
# identical resumes/jobs pdf_extraction.py implementations; and the fakes
# below are intentionally minimal single-purpose stand-ins.
# pylint: disable=duplicate-code,too-few-public-methods

import logging

import pytest
from pdfminer.pdfparser import PDFSyntaxError

from .services import pdf_extraction


class FakePage:
    """Stands in for a pdfplumber page, exposing only extract_text()."""

    def __init__(self, text):
        self.text = text

    def extract_text(self):
        """Return the fixed page text, matching Page.extract_text()."""
        return self.text


class FakePdf:
    """Stands in for pdfplumber's PDF context manager, exposing only .pages."""

    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """Match pdfplumber.PDF's context manager protocol; nothing to clean up."""
        return False


class FakeTempStorage:
    """Stands in for temp_storage, recording delete() calls and optionally failing."""

    def __init__(self, delete_exception=None):
        self.delete_exception = delete_exception
        self.deleted = []

    def delete(self, name):
        """Record the delete call and raise delete_exception if configured."""
        self.deleted.append(name)
        if self.delete_exception is not None:
            raise self.delete_exception


def patch_pipeline(monkeypatch, *, open_exception=None, pages_text=("extracted text",)):
    """Replace pdfplumber.open with a controllable fake."""

    def fake_open(path):  # pylint: disable=unused-argument
        if open_exception is not None:
            raise open_exception
        return FakePdf([FakePage(text) for text in pages_text])

    monkeypatch.setattr(pdf_extraction.pdfplumber, "open", fake_open)


def patch_temp_storage(
    monkeypatch, *, delete_exception=None, name="fake.pdf", path="/tmp/fake.pdf"
):
    """Replace get_temp_pdf_path/temp_storage with controllable fakes."""
    fake_storage = FakeTempStorage(delete_exception)
    monkeypatch.setattr(pdf_extraction, "get_temp_pdf_path", lambda pdf_file: (name, path))
    monkeypatch.setattr(pdf_extraction, "temp_storage", fake_storage)
    return fake_storage


def test_successful_extraction_returns_text_and_cleans_up(monkeypatch):
    """Extraction succeeds and the temp file is deleted afterward."""
    patch_pipeline(monkeypatch, pages_text=("Resume\nSkills: Python",))
    fake_storage = patch_temp_storage(monkeypatch)

    result = pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert result == "Resume\nSkills: Python"
    assert fake_storage.deleted == ["fake.pdf"]


def test_successful_extraction_joins_multiple_pages(monkeypatch):
    """Extraction concatenates text from every page, separated by a blank line."""
    patch_pipeline(monkeypatch, pages_text=("page one", "page two"))
    patch_temp_storage(monkeypatch)

    result = pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert result == "page one\n\npage two"


def test_parse_error_becomes_pdf_extraction_error(monkeypatch):
    """A PDFSyntaxError from pdfplumber degrades to a clean PdfExtractionError."""
    patch_pipeline(monkeypatch, open_exception=PDFSyntaxError("bad structure"))
    fake_storage = patch_temp_storage(monkeypatch)

    with pytest.raises(
        pdf_extraction.PdfExtractionError, match="corrompido ou protegido por senha"
    ):
        pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert fake_storage.deleted == ["fake.pdf"]


def test_non_parse_error_from_pdfplumber_is_not_swallowed(monkeypatch):
    """A pdfplumber bug unrelated to parsing must propagate as-is, not as PdfExtractionError."""
    patch_pipeline(monkeypatch, open_exception=AttributeError("internal pdfplumber bug"))
    patch_temp_storage(monkeypatch)

    with pytest.raises(AttributeError, match="internal pdfplumber bug"):
        pdf_extraction.extract_text_from_pdf(pdf_file=object())


def test_empty_text_raises_pdf_extraction_error(monkeypatch):
    """Whitespace-only extracted text degrades to a clean PdfExtractionError."""
    patch_pipeline(monkeypatch, pages_text=("   ",))
    fake_storage = patch_temp_storage(monkeypatch)

    with pytest.raises(pdf_extraction.PdfExtractionError, match="texto utilizável"):
        pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert fake_storage.deleted == ["fake.pdf"]


def test_temp_file_save_failure_becomes_pdf_extraction_error(monkeypatch):
    """A failed temp-file save degrades to a clean PdfExtractionError."""

    def raise_oserror(pdf_file):
        raise OSError("disk full")

    monkeypatch.setattr(pdf_extraction, "get_temp_pdf_path", raise_oserror)

    with pytest.raises(pdf_extraction.PdfExtractionError, match="salvar o PDF"):
        pdf_extraction.extract_text_from_pdf(pdf_file=object())


def test_temp_file_delete_failure_does_not_mask_parse_error(monkeypatch, caplog):
    """A failed cleanup must not replace the real parse error with an OSError."""
    patch_pipeline(monkeypatch, open_exception=PDFSyntaxError("bad structure"))
    patch_temp_storage(monkeypatch, delete_exception=OSError("permission denied"))

    with caplog.at_level(logging.WARNING):
        with pytest.raises(
            pdf_extraction.PdfExtractionError, match="corrompido ou protegido por senha"
        ):
            pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert "failed to delete temp file" in caplog.text


def test_temp_file_delete_failure_does_not_break_happy_path(monkeypatch, caplog):
    """A failed temp-file delete logs a warning but does not break a successful extraction."""
    patch_pipeline(monkeypatch, pages_text=("Resume",))
    patch_temp_storage(monkeypatch, delete_exception=OSError("permission denied"))

    with caplog.at_level(logging.WARNING):
        result = pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert result == "Resume"
    assert "failed to delete temp file" in caplog.text
