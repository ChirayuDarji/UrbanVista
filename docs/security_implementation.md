# Security Implementation - UrbanSite

## Overview
This document outlines all security measures implemented in the UrbanSite Django project.

## 1. Secure Django Settings

### Environment Variables (.env file)
- **SECRET_KEY**: Moved to environment variable
- **DEBUG**: Controlled via environment variable (False in production)
- **ALLOWED_HOSTS**: Configured via environment variable
- **Database credentials**: Stored in environment variables
- **Email credentials**: Stored in environment variables

### Security Headers
- `SECURE_BROWSER_XSS_FILTER = True` - Enables browser XSS filtering
- `SECURE_CONTENT_TYPE_NOSNIFF = True` - Prevents MIME type sniffing
- `X_FRAME_OPTIONS = 'DENY'` - Prevents clickjacking attacks
- `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"` - Controls referrer information

## 2. HTTPS & SSL Enforcement

### Production Settings
- `SECURE_SSL_REDIRECT = True` - Redirects HTTP to HTTPS
- `SESSION_COOKIE_SECURE = True` - Only sends session cookies over HTTPS
- `CSRF_COOKIE_SECURE = True` - Only sends CSRF cookies over HTTPS
- `SECURE_HSTS_SECONDS = 31536000` - HSTS header (1 year)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` - Include subdomains in HSTS
- `SECURE_HSTS_PRELOAD = True` - Enable HSTS preload

## 3. File Upload Security

### Validation Rules
- **Size limit**: Maximum 5MB per file
- **File type**: Only image files allowed (JPG, PNG, GIF, BMP, WebP)
- **Extension whitelist**: Only safe extensions permitted
- **Dangerous extensions blocked**: `.exe`, `.bat`, `.js`, `.php`, etc.
- **Magic byte validation**: Checks file signatures to prevent MIME spoofing

### Implementation
- Located in `UrbanSite/security.py`
- `validate_file_upload()` function performs comprehensive checks

## 4. Spam & Abuse Protection

### Rate Limiting
- **Django cache-based**: Uses `django.core.cache` for distributed rate limiting
- **IP-based**: 1 submission per IP every 5 minutes
- **Email-based**: 1 submission per email every 5 minutes
- **Configurable**: Time window and max requests can be adjusted

### Keyword Filtering
- **Spam detection**: Checks content for inappropriate keywords
- **False positive protection**: Allows technical terms (hackathon, etc.)
- **User-friendly errors**: Clear messages when spam detected

### Implementation
- Rate limiting: `UrbanSite/security.py::check_rate_limit()`
- Keyword filtering: `UrbanSite/security.py::validate_content_for_spam()`
- Applied in: `UrbanSite/forms.py` and `UrbanSite/views.py`

## 5. Admin & Access Control

### Admin URL Security
- **Changed admin URL**: `/admin/` → `/urbansite-admin/`
- **Redirect**: Old URL redirects to new one (can be removed in production)

### Password Security
- **Minimum length**: 12 characters (increased from default 8)
- **Complexity requirements**: 
  - UserAttributeSimilarityValidator
  - CommonPasswordValidator
  - NumericPasswordValidator

### Admin Security Features
- **IP logging**: All admin actions logged with IP addresses
- **Security auditing**: Logs all create/update/delete operations
- **Read-only fields**: Sensitive fields (IP, timestamps) are read-only

## 6. Backup & Data Protection

### Backup Command
- **Location**: `UrbanSite/management/commands/backup_data.py`
- **Usage**: `python manage.py backup_data`
- **Options**:
  - `--media-only`: Backup only media files
  - `--db-only`: Backup only database
  - `--output-dir`: Custom output directory

### Backup Retention
- **Database backups**: Keeps last 7 backups (weekly retention)
- **Media backups**: Keeps last 4 backups (monthly retention)
- **Automatic cleanup**: Old backups removed automatically

### Scheduled Backups
- Can be scheduled via cron (Linux) or Task Scheduler (Windows)
- Example cron: `0 2 * * 0 cd /path/to/project && python manage.py backup_data`

## 7. Logging & Monitoring

### Log Files
- **Django logs**: `logs/django.log`
- **Security logs**: `logs/security.log`

### Logged Events
- **Report submissions**: All successful submissions logged
- **Rate limit violations**: IP and email rate limit violations
- **Admin actions**: All admin create/update/delete operations
- **Failed login attempts**: (via Django security logger)
- **Spam detection**: Content flagged as spam

### Log Levels
- **INFO**: Normal operations (report submissions, admin actions)
- **WARNING**: Rate limit violations, suspicious activity
- **ERROR**: Security errors, validation failures

## 8. Additional Security Measures

### CSRF Protection
- Enabled by default via Django middleware
- Secure cookies in production (HTTPS only)

### Session Security
- Secure cookies in production
- Session timeout configured

### Content Security
- XSS protection enabled
- Content type sniffing disabled
- Clickjacking protection enabled

## Testing Security Features

### Manual Tests
1. **File Upload**: Try uploading a large file (>5MB) → Should be rejected
2. **File Type**: Try uploading `.exe` or `.php` file → Should be rejected
3. **Rate Limiting**: Submit multiple reports from same IP → Should be blocked after first
4. **Spam Detection**: Submit report with spam keywords → Should be rejected
5. **Admin Access**: Try accessing `/admin/` → Should redirect to `/urbansite-admin/`

### Automated Tests
- All security features are tested in `UrbanSite/tests/`
- File upload validation tests
- Rate limiting tests
- Spam detection tests

## Production Deployment Checklist

- [ ] Set `DEBUG = False` in environment
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Configure `ALLOWED_HOSTS` with production domain
- [ ] Set strong `DJANGO_SECRET_KEY` in environment
- [ ] Configure database credentials in environment
- [ ] Configure email SMTP settings in environment
- [ ] Set up SSL certificate
- [ ] Configure HSTS settings
- [ ] Set up scheduled backups (cron/Task Scheduler)
- [ ] Review and update spam keywords list
- [ ] Monitor security logs regularly
- [ ] Remove `/admin/` redirect (keep only `/urbansite-admin/`)

## Security Notes

1. **Security through obscurity**: Changing admin URL helps but is not primary security
2. **Rate limiting**: Uses Django cache (can be upgraded to Redis for production)
3. **File validation**: Magic byte checking helps prevent MIME spoofing
4. **Logging**: All security events are logged for audit trail
5. **Backups**: Regular backups protect against data loss

## Future Enhancements

- [ ] Implement 2FA for admin users (django-two-factor-auth)
- [ ] Add reCAPTCHA integration
- [ ] Implement IP whitelisting for admin
- [ ] Add failed login attempt tracking
- [ ] Implement password history (prevent reuse)
- [ ] Add audit log viewer in admin
- [ ] Implement automated security scanning

