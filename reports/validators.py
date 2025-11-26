# reports/validators.py
from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
MAX_IMAGE_MB = 5

def validate_image_file(file):
    if not file:
        return
    ext = (file.name or "").lower().rsplit(".", 1)[-1]
    if f".{ext}" not in ALLOWED_IMAGE_EXTS:
        raise ValidationError("Only JPG, JPEG, or PNG images are allowed.")
    size_mb = file.size / (1024 * 1024)
    if size_mb > MAX_IMAGE_MB:
        raise ValidationError(f"Image must be under {MAX_IMAGE_MB} MB.")

def has_spam_keywords(text: str):
    spam_words = ["test", "testing", "fake", "spam", "asdf", "qwerty"]
    lowered = (text or "").lower()
    return any(word in lowered for word in spam_words)