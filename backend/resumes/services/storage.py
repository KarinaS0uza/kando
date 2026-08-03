"""Temporary file storage helpers for PDF processing."""
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage

temp_storage = FileSystemStorage(location=settings.MEDIA_ROOT / "tmp")


def get_temp_pdf_path(pdf_file) -> tuple[str, str]:
    """Save an uploaded PDF to temporary storage and return its name and path.

    Args:
        pdf_file (django.core.files.uploadedfile.UploadedFile): PDF file
            uploaded through the API request.

    Returns:
        A tuple of ``(name, path)`` for the saved temporary file. The name
        is the key used to delete it later via ``temp_storage``.
    """
    name = temp_storage.save(f"{uuid.uuid4()}.pdf", pdf_file)
    return name, temp_storage.path(name)
