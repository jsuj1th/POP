#!/usr/bin/env python
"""
TAMU OIDC Configuration Diagnostic Script
Run this to verify your OIDC setup is correct
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pop_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
import requests

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_oidc_settings():
    print_section("1. OIDC Settings Check")
    
    checks = [
        ("Client ID", settings.OIDC_RP_CLIENT_ID),
        ("Client Secret", settings.OIDC_RP_CLIENT_SECRET),
        ("Authorization Endpoint", settings.OIDC_OP_AUTHORIZATION_ENDPOINT),
        ("Token Endpoint", settings.OIDC_OP_TOKEN_ENDPOINT),
        ("User Endpoint", settings.OIDC_OP_USER_ENDPOINT),
        ("JWKS Endpoint", settings.OIDC_OP_JWKS_ENDPOINT),
    ]
    
    issues = []
    for name, value in checks:
        if not value:
            status = "❌ MISSING"
            issues.append(name)
        elif len(str(value)) > 50:
            display = str(value)[:47] + "..."
            status = f"✅ {display}"
        else:
            status = f"✅ {value}"
        
        print(f"  {name:25} {status}")
    
    return issues

def check_endpoints():
    print_section("2. Azure AD Endpoint Connectivity")
    
    endpoints = [
        ("JWKS", settings.OIDC_OP_JWKS_ENDPOINT),
        ("Authorization", settings.OIDC_OP_AUTHORIZATION_ENDPOINT),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5, verify=settings.OIDC_VERIFY_SSL)
            if response.status_code == 200:
                print(f"  ✅ {name:20} ({response.status_code})")
            else:
                print(f"  ⚠️  {name:20} ({response.status_code})")
        except Exception as e:
            print(f"  ❌ {name:20} Error: {str(e)[:40]}")

def check_authentication_backend():
    print_section("3. Authentication Backend Check")
    
    backends = settings.AUTHENTICATION_BACKENDS
    print(f"  Configured backends:")
    for i, backend in enumerate(backends, 1):
        if 'TAMU' in backend:
            print(f"    {i}. ✅ {backend} (Custom TAMU)")
        elif 'ModelBackend' in backend:
            print(f"    {i}. ✅ {backend} (Fallback)")
        else:
            print(f"    {i}. {backend}")

def check_installed_apps():
    print_section("4. Installed Apps Check")
    
    required_app = 'mozilla_django_oidc'
    if required_app in settings.INSTALLED_APPS:
        print(f"  ✅ {required_app} is installed")
    else:
        print(f"  ❌ {required_app} is NOT installed")
        print(f"     Add 'mozilla_django_oidc' to INSTALLED_APPS in settings.py")

def check_urls():
    print_section("5. URL Configuration Check")
    
    from django.urls import get_resolver
    resolver = get_resolver()
    
    oidc_routes = []
    for pattern in resolver.url_patterns:
        if 'oidc' in str(pattern.pattern):
            oidc_routes.append(str(pattern.pattern))
    
    if oidc_routes:
        print(f"  ✅ OIDC routes found:")
        for route in oidc_routes:
            print(f"     - {route}")
    else:
        print(f"  ❌ No OIDC routes found!")
        print(f"     Add to urls.py: path('oidc/', include('mozilla_django_oidc.urls'))")

def check_redirect_uri():
    print_section("6. Redirect URI Check")
    
    print(f"  Expected redirect URI for Azure Portal:")
    print(f"  📍 http://localhost:8000/oidc/callback/")
    print(f"\n  Make sure this is added to your app registration:")
    print(f"  Azure Portal → App Registration → Authentication → Platform configs")

def check_tenant_id():
    print_section("7. Tenant ID Check")
    
    auth_endpoint = settings.OIDC_OP_AUTHORIZATION_ENDPOINT
    
    if '/common/' in auth_endpoint:
        print(f"  ⚠️  Using '/common/' tenant endpoint")
        print(f"     This works but is not ideal for production")
        print(f"\n  Recommendation:")
        print(f"  1. Go to Azure Portal → Azure Active Directory")
        print(f"  2. Copy the 'Tenant ID' (Directory ID)")
        print(f"  3. Update .env with specific tenant:")
        print(f"     OIDC_OP_AUTHORIZATION_ENDPOINT=https://login.microsoftonline.com/[TENANT-ID]/oauth2/v2.0/authorize")
        print(f"     OIDC_OP_TOKEN_ENDPOINT=https://login.microsoftonline.com/[TENANT-ID]/oauth2/v2.0/token")
    else:
        if 'common' not in auth_endpoint:
            print(f"  ✅ Using specific tenant ID")
        else:
            print(f"  Tenant endpoint: {auth_endpoint}")

def main():
    print("\n" + "="*60)
    print("  🔧 TAMU OIDC Configuration Diagnostic")
    print("="*60)
    
    # Run all checks
    settings_issues = check_oidc_settings()
    check_endpoints()
    check_authentication_backend()
    check_installed_apps()
    check_urls()
    check_redirect_uri()
    check_tenant_id()
    
    # Summary
    print_section("Summary & Next Steps")
    
    if settings_issues:
        print(f"\n  ❌ Issues found:\n")
        for issue in settings_issues:
            print(f"     - {issue} is missing or empty")
        print(f"\n  ✅ To fix:")
        print(f"     1. Edit .env file")
        print(f"     2. Add missing values from Azure Portal")
        print(f"     3. Save the file")
        print(f"     4. Restart Django: python manage.py runserver")
    else:
        print(f"\n  ✅ All settings look good!")
        print(f"\n  📋 To test:")
        print(f"     1. python manage.py runserver")
        print(f"     2. Visit http://localhost:8000/login/")
        print(f"     3. Click 'Sign in with TAMU' button")
        print(f"     4. You should be redirected to login.microsoftonline.com")
    
    print(f"\n  📖 For more help, see: AZURE_CONFIG_TROUBLESHOOTING.md")
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error running diagnostic: {e}")
        import traceback
        traceback.print_exc()
