"""
TAMU OIDC Authentication Backend
Extends mozilla-django-oidc to handle TAMU-specific claims
"""

from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class TAMUOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Custom OIDC backend for TAMU authentication.
    Handles mapping of Azure AD claims to Django user fields.
    """

    def create_user(self, claims):
        """
        Create a new user based on Azure AD claims.
        
        Args:
            claims: Dictionary of user claims from Azure AD
            
        Returns:
            New user instance
        """
        user = super().create_user(claims)
        return self.update_user(user, claims)

    def update_user(self, user, claims):
        """
        Update user information from Azure AD claims.
        
        Args:
            user: User instance to update
            claims: Dictionary of user claims from Azure AD
            
        Returns:
            Updated user instance
        """
        # Map Azure AD claims to Django user fields
        user.email = claims.get('email', '')
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        
        # TAMU specific: Extract NetID from email if available
        if '@tamu.edu' in user.email:
            user.username = user.email.split('@')[0]
        elif user.email:
            user.username = user.email.split('@')[0]
        
        user.save()
        return user

    def user_claims_verifier(self, claims):
        """
        Verify user claims are valid.
        
        Args:
            claims: Dictionary of user claims
            
        Returns:
            True if claims are valid, False otherwise
        """
        # Optionally verify email domain is @tamu.edu
        email = claims.get('email', '')
        
        # Allow both tamu.edu and any email domain
        # Uncomment the line below to restrict to TAMU only:
        # return email.endswith('@tamu.edu')
        
        return bool(email)
