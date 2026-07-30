
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage

temp_storage = FileSystemStorage(location=settings.MEDIA_ROOT / "tmp")


def get_temp_pdf_path(pdf_file) -> tuple[str, str]:
    name = temp_storage.save(f"{uuid.uuid4()}.pdf", pdf_file)
    return name, temp_storage.path(name)