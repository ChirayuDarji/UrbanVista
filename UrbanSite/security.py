# UrbanSite/security.py
"""
Security utilities for UrbanSite app:
- File upload validation
- Keyword filtering for spam
- Rate limiting
"""
import os
import hashlib
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# ============================================================================
# FILE UPLOAD SECURITY
# ============================================================================

# Allowed image file extensions (whitelist approach)
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

# Dangerous file extensions that should be rejected
DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.app', '.deb', '.pkg', '.rpm', '.sh', '.ps1', '.py', '.php', '.asp',
    '.aspx', '.jsp', '.rb', '.pl', '.cgi', '.dll', '.so', '.dylib'
}

# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_file_upload(file):
    """
    Comprehensive file upload validation:
    - Size limit (5MB)
    - File type (images only)
    - Reject dangerous extensions
    - Check file signature (magic bytes)
    
    Args:
        file: UploadedFile object
        
    Raises:
        ValidationError: If file is invalid or dangerous
    """
    if not file:
        return
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024):.1f}MB"
        )
    
    # Get file extension
    file_name = file.name.lower()
    file_ext = os.path.splitext(file_name)[1]
    
    # Reject dangerous extensions
    if file_ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(
            f"File type '{file_ext}' is not allowed for security reasons. "
            "Only image files are permitted."
        )
    
    # Check if it's an allowed image extension
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Invalid file type. Only image files ({', '.join(ALLOWED_IMAGE_EXTENSIONS)}) are allowed."
        )
    
    # Check content type
    if hasattr(file, 'content_type'):
        if not file.content_type or not file.content_type.startswith('image/'):
            raise ValidationError("File must be an image. Invalid content type detected.")
    
    # Basic magic byte check (first few bytes)
    # This helps prevent MIME type spoofing
    if hasattr(file, 'read'):
        try:
            file.seek(0)
            magic_bytes = file.read(8)
            file.seek(0)
            
            # Check for common image file signatures
            is_valid_image = False
            if magic_bytes.startswith(b'\xFF\xD8\xFF'):  # JPEG
                is_valid_image = True
            elif magic_bytes.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                is_valid_image = True
            elif magic_bytes.startswith(b'GIF87a') or magic_bytes.startswith(b'GIF89a'):  # GIF
                is_valid_image = True
            elif magic_bytes.startswith(b'BM'):  # BMP
                is_valid_image = True
            elif magic_bytes.startswith(b'RIFF') and b'WEBP' in magic_bytes:  # WebP
                is_valid_image = True
            
            if not is_valid_image and file_ext in ALLOWED_IMAGE_EXTENSIONS:
                # File extension says it's an image but magic bytes don't match
                raise ValidationError(
                    "File content does not match file extension. "
                    "This may indicate a security risk."
                )
        except Exception as e:
            # If we can't read the file, reject it
            raise ValidationError(f"Unable to validate file: {str(e)}")


# ============================================================================
# KEYWORD FILTERING (Spam Protection)
# ============================================================================

# List of inappropriate/spam keywords (case-insensitive)
SPAM_KEYWORDS = [
    # Common spam words
    'viagra', 'cialis', 'casino', 'poker', 'lottery', 'winner',
    'click here', 'buy now', 'limited time', 'act now',
    # Inappropriate content
    'hack', 'crack', 'warez', 'porn', 'xxx',
    # Scam indicators
    'nigerian prince', 'inheritance', 'free money', 'get rich quick',
    # Add more as needed
]

# Words that might be false positives (allow these)
ALLOWED_WORDS = [
    'hackerrank', 'hackathon',  # Technical terms
    'cracked', 'cracking',      # Technical terms (code cracking, etc.)
]


def contains_spam_keywords(text):
    """
    Check if text contains spam or inappropriate keywords.
    
    Args:
        text: String to check
        
    Returns:
        tuple: (is_spam: bool, matched_keywords: list)
    """
    if not text:
        return False, []
    
    text_lower = text.lower()
    matched_keywords = []
    
    for keyword in SPAM_KEYWORDS:
        keyword_lower = keyword.lower()
        # Check if keyword is in text but not as part of an allowed word
        if keyword_lower in text_lower:
            # Check if it's part of an allowed word
            is_allowed = False
            for allowed in ALLOWED_WORDS:
                if keyword_lower in allowed.lower() and allowed.lower() in text_lower:
                    is_allowed = True
                    break
            
            if not is_allowed:
                matched_keywords.append(keyword)
    
    return len(matched_keywords) > 0, matched_keywords


def validate_content_for_spam(text, field_name="content"):
    """
    Validate content and raise error if spam detected.
    
    Args:
        text: Content to validate
        field_name: Name of the field (for error message)
        
    Raises:
        ValidationError: If spam content detected
    """
    is_spam, keywords = contains_spam_keywords(text)
    
    if is_spam:
        raise ValidationError(
            f"The {field_name} contains inappropriate content and cannot be submitted. "
            f"Please review and remove any spam or inappropriate language."
        )


# ============================================================================
# RATE LIMITING (using Django cache)
# ============================================================================

def get_rate_limit_key(identifier, action="report_submission"):
    """
    Generate cache key for rate limiting.
    
    Args:
        identifier: IP address or email
        action: Type of action being rate limited
        
    Returns:
        str: Cache key
    """
    return f"rate_limit:{action}:{identifier}"


def check_rate_limit(identifier, max_requests=1, time_window=300, action="report_submission"):
    """
    Check if identifier has exceeded rate limit.
    Uses Django cache for distributed rate limiting.
    
    Args:
        identifier: IP address or email
        max_requests: Maximum requests allowed
        time_window: Time window in seconds (default: 5 minutes)
        action: Type of action being rate limited
        
    Returns:
        tuple: (is_allowed: bool, time_remaining: int)
    """
    cache_key = get_rate_limit_key(identifier, action)
    
    # Get current count from cache
    current_count = cache.get(cache_key, 0)
    
    if current_count >= max_requests:
        # Rate limit exceeded
        # Get remaining time
        ttl = cache.ttl(cache_key)
        time_remaining = ttl if ttl > 0 else 0
        return False, time_remaining
    
    # Increment counter
    cache.set(cache_key, current_count + 1, time_window)
    
    return True, 0


def reset_rate_limit(identifier, action="report_submission"):
    """
    Reset rate limit for an identifier (useful for testing or admin actions).
    
    Args:
        identifier: IP address or email
        action: Type of action
    """
    cache_key = get_rate_limit_key(identifier, action)
    cache.delete(cache_key)


# ============================================================================
# IP ADDRESS UTILITIES
# ============================================================================

def get_client_ip(request):
    """
    Get client IP address from request, handling proxies.
    
    Args:
        request: Django request object
        
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip or 'unknown'

