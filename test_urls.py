#!/usr/bin/env python
"""
Quick URL testing script to verify all routes are accessible.
Run: python test_urls.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.conf import settings

def test_urls():
    """Test all URL patterns"""
    # Add testserver to ALLOWED_HOSTS for testing
    original_allowed_hosts = settings.ALLOWED_HOSTS
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']
    
    client = Client()
    urls_to_test = [
        # Main pages
        ('home', {}),
        ('about', {}),
        ('help_center', {}),
        
        # Auth
        ('account_login', {}),
        ('account_signup', {}),
        
        # Reports
        ('reports:report_list', {}),
        ('reports:statistics', {}),
        ('reports:leaderboard', {}),
        
        # News
        ('news:list', {}),
        
        # Projects
        ('projects:list', {}),
        
        # Contribute
        ('freecontribution:experience_home', {}),
    ]
    
    print("=" * 60)
    print("URL TESTING REPORT")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for url_name, kwargs in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url, follow=True)
            
            if response.status_code in [200, 302, 301]:
                print(f"✅ {url_name:40} -> {url:50} [{response.status_code}]")
                passed += 1
            else:
                print(f"❌ {url_name:40} -> {url:50} [{response.status_code}]")
                failed += 1
        except NoReverseMatch as e:
            print(f"⚠️  {url_name:40} -> URL not found: {str(e)}")
            skipped += 1
        except Exception as e:
            print(f"❌ {url_name:40} -> Error: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: ✅ {passed} passed | ❌ {failed} failed | ⚠️  {skipped} skipped")
    print("=" * 60)
    
    # Restore original ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = original_allowed_hosts
    
    return failed == 0

if __name__ == '__main__':
    success = test_urls()
    sys.exit(0 if success else 1)

