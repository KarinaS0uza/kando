"""Unit tests for jobs.services.pdf_extraction: conversion and I/O failure paths."""

# Mirrors resumes/test_pdf_extraction.py by design, since it exercises the
# identical resumes/jobs pdf_extraction.py implementations; and the fakes
# below are intentionally minimal single-purpose stand-ins.
# pylint: disable=duplicate-code,too-few-public-methods

import logging

import pytest
from docling.exceptions import ConversionError

from .services import pdf_extraction


class FakeSerializedText:
    """Stands in for MarkdownDocSerializer().serialize() return value."""

    def __init__(self, text):
        self.text = text


class FakeSerializer:
    """Stands in for MarkdownDocSerializer, returning a fixed markdown text."""

    def __init__(self, markdown_text):
        self.markdown_text = markdown_text

    def __call__(self, doc, params):
        """Match the MarkdownDocSerializer(doc=..., params=...) constructor call."""
        return self

    def serialize(self):
        """Return the fixed markdown text, matching MarkdownDocSerializer.serialize()."""
        return FakeSerializedText(self.markdown_text)


class FakeConversionResult:
    """Stands in for docling's ConversionResult, exposing only .document."""

    document = object()


class FakeConverter:
    """Stands in for DocumentConverter, raising or returning a fixed result."""

    def __init__(self, convert_exception=None):
        self.convert_exception = convert_exception

    def convert(self, path):  # pylint: disable=unused-argument
        """Match DocumentConverter.convert(path): raise or return a fixed result."""
        if self.convert_exception is not None:
            raise self.convert_exception
        return FakeConversionResult()


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


def patch_pipeline(monkeypatch, *, convert_exception=None, markdown_text="extracted text"):
    """Replace DocumentConverter/MarkdownDocSerializer with controllable fakes."""
    monkeypatch.setattr(
        pdf_extraction, "DocumentConverter", lambda **kwargs: FakeConverter(convert_exception)
    )
    monkeypatch.setattr(pdf_extraction, "MarkdownDocSerializer", FakeSerializer(markdown_text))


def patch_temp_storage(
    monkeypatch, *, delete_exception=None, name="fake.pdf", path="/tmp/fake.pdf"
):
    """Replace get_temp_pdf_path/temp_storage with controllable fakes."""
    fake_storage = FakeTempStorage(delete_exception)
    monkeypatch.setattr(pdf_extraction, "get_temp_pdf_path", lambda pdf_file: (name, path))
    monkeypatch.setattr(pdf_extraction, "temp_storage", fake_storage)
    return fake_storage


def test_successful_extraction_returns_markdown_and_cleans_up(monkeypatch):
    """Extraction succeeds and the temp file is deleted afterward."""
    patch_pipeline(monkeypatch, markdown_text="# Resume\nSkills: Python")
    fake_storage = patch_temp_storage(monkeypatch)

    result = pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert result == "# Resume\nSkills: Python"
    assert fake_storage.deleted == ["fake.pdf"]


def test_conversion_error_becomes_pdf_extraction_error(monkeypatch):
    """A ConversionError from docling degrades to a clean PdfExtractionError."""
    patch_pipeline(monkeypatch, convert_exception=ConversionError("bad structure"))
    fake_storage = patch_temp_storage(monkeypatch)

    with pytest.raises(
        pdf_extraction.PdfExtractionError, match="corrompido ou protegido por senha"
    ):
        pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert fake_storage.deleted == ["fake.pdf"]


def test_non_conversion_error_from_docling_is_not_swallowed(monkeypatch):
    """A docling bug unrelated to conversion must propagate as-is, not as PdfExtractionError."""
    patch_pipeline(monkeypatch, convert_exception=AttributeError("internal docling bug"))
    patch_temp_storage(monkeypatch)

    with pytest.raises(AttributeError, match="internal docling bug"):
        pdf_extraction.extract_text_from_pdf(pdf_file=object())


def test_empty_markdown_raises_pdf_extraction_error(monkeypatch):
    """Whitespace-only extracted markdown degrades to a clean PdfExtractionError."""
    patch_pipeline(monkeypatch, markdown_text="   ")
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


def test_temp_file_delete_failure_does_not_mask_conversion_error(monkeypatch, caplog):
    """A failed cleanup must not replace the real conversion error with an OSError."""
    patch_pipeline(monkeypatch, convert_exception=ConversionError("bad structure"))
    patch_temp_storage(monkeypatch, delete_exception=OSError("permission denied"))

    with caplog.at_level(logging.WARNING):
        with pytest.raises(
            pdf_extraction.PdfExtractionError, match="corrompido ou protegido por senha"
        ):
            pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert "failed to delete temp file" in caplog.text


def test_temp_file_delete_failure_does_not_break_happy_path(monkeypatch, caplog):
    """A failed temp-file delete logs a warning but does not break a successful extraction."""
    patch_pipeline(monkeypatch, markdown_text="# Resume")
    patch_temp_storage(monkeypatch, delete_exception=OSError("permission denied"))

    with caplog.at_level(logging.WARNING):
        result = pdf_extraction.extract_text_from_pdf(pdf_file=object())

    assert result == "# Resume"
    assert "failed to delete temp file" in caplog.text
