# reports/spam_detector.py
from django.utils import timezone
from django.db.models import Q
import re
from .models import IssueReport

def check_spam(user, data):
    """
    Returns: (is_block: bool, spam_score: int, reasons: list[str], decision: str)
    decision = one of: CLEAN, SUSPICIOUS, LIKELY, DEFINITE
    """
    score = 0
    reasons = []

    # 1) Rate limiting (>=3 today)
    today = timezone.localdate()
    daily = IssueReport.objects.filter(user=user, submitted_at__date=today).count()
    if daily >= 3:
        score += 25
        reasons.append("Daily limit exceeded")

    # 2) Duplicate (same category+ward within 24h)
    last_24h = timezone.now() - timezone.timedelta(hours=24)
    dup_exists = IssueReport.objects.filter(
        user=user,
        category=data.get("category"),
        ward=data.get("ward"),
        submitted_at__gte=last_24h,
    ).exists()
    if dup_exists:
        score += 30
        reasons.append("Duplicate report detected")

    # 3) Content quality
    desc = (data.get("description") or "")
    title = (data.get("title") or "")
    if len(desc.strip()) < 50:
        score += 15
        reasons.append("Short description (<50 chars)")

    spam_words = ["test", "testing", "fake", "spam", "asdf", "qwerty"]
    for w in spam_words:
        if w in desc.lower() or w in title.lower():
            score += 20
            reasons.append(f"Spam keyword: {w}")

    if re.search(r"[@#]{4,}", desc):
        score += 15
        reasons.append("Excessive special characters")

    # ALL CAPS > 50% check for title+desc
    combined = f"{title} {desc}".strip()
    if combined and sum(1 for c in combined if c.isupper()) > 0.5 * len([c for c in combined if c.isalpha()]):
        score += 10
        reasons.append("ALL CAPS content")

    # repeated words (>=5 times)
    words = re.findall(r"\b\w+\b", desc.lower())
    if words:
        from collections import Counter
        c = Counter(words)
        if any(freq >= 5 for freq in c.values()):
            score += 15
            reasons.append("Repeated words")

    # 4) New user flag (account < 3 days)
    profile = getattr(user, "profile", None)
    if profile and hasattr(profile, "is_new_user") and callable(getattr(profile, "is_new_user", None)):
        try:
            if profile.is_new_user():
                score += 10
                reasons.append("New user - needs review")
        except Exception:
            pass
    elif hasattr(user, "date_joined"):
        # Fallback: check if user joined within last 3 days
        from datetime import timedelta
        try:
            if timezone.now() - user.date_joined < timedelta(days=3):
                score += 10
                reasons.append("New user - needs review")
        except Exception:
            pass

    # 5) Ward mismatch across zones (light flag)
    if profile and data.get("ward"):
        try:
            profile_ward = getattr(profile, "ward", None)
            ward_obj = data.get("ward")
            if profile_ward and ward_obj and hasattr(ward_obj, "zone") and hasattr(profile_ward, "zone"):
                if profile_ward.zone != ward_obj.zone:
                    score += 5
                    reasons.append("Reporting outside home area")
        except Exception:
            pass

    # 6) Image validation
    img1 = data.get("image1")
    if not img1:
        score += 40
        reasons.append("No image attached")
    else:
        if getattr(img1, "size", 0) < 50 * 1024:
            score += 10
            reasons.append("Image too small (<50KB)")

    # Decision buckets
    if score <= 15:
        decision = "CLEAN"
        is_block = False
    elif 16 <= score <= 35:
        decision = "SUSPICIOUS"
        is_block = False
    elif 36 <= score <= 50:
        decision = "LIKELY"
        is_block = False  # hold for manual review, but not block submission
    else:
        decision = "DEFINITE"
        is_block = True

    return is_block, score, reasons, decision