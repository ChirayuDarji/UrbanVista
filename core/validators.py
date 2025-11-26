from __future__ import annotations

import os
from django.core.exceptions import ValidationError


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".ps1", ".php", ".js"}


def validate_file_size(file, max_size: int) -> None:
    if not file:
        return
    if file.size > max_size:
        raise ValidationError(f"File size exceeds {max_size // (1024 * 1024)}MB")


def validate_image_file(file, *, max_size: int = 5 * 1024 * 1024) -> None:
    if not file:
        return

    validate_file_size(file, max_size)

    name = (file.name or "").lower()
    ext = os.path.splitext(name)[1]

    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError("This file type is not allowed")

    if ext not in IMAGE_EXTENSIONS:
        raise ValidationError("Only image files are allowed")

    content_type = getattr(file, "content_type", "") or ""
    if not content_type.startswith("image/"):
        raise ValidationError("Invalid content type; expected image/*")


