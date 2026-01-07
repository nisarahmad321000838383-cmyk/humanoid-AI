"""
Custom JWT Authentication that reads tokens from HTTP-only cookies
and validates against the auth_tokens table.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that:
    1. Reads the access token from cookies instead of the Authorization header
    2. Validates the token exists in the auth_tokens table and is not revoked
    """
    
    def authenticate(self, request):
        # First try to get token from cookie
        raw_token = request.COOKIES.get('access_token')
        
        # If no cookie, fall back to header-based auth (for backwards compatibility)
        if raw_token is None:
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
        
        if raw_token is None:
            return None
        
        # Validate JWT signature and expiry
        validated_token = self.get_validated_token(raw_token)
        
        # Additional validation: Check if token exists in database and is valid
        from accounts.models import AuthToken
        token_hash = AuthToken.hash_token(raw_token)
        
        db_token = AuthToken.objects.filter(
            token_hash=token_hash,
            token_type='access'
        ).first()
        
        # If token not found in database, it's been deleted (logged out)
        if not db_token:
            raise AuthenticationFailed('Token has been revoked or does not exist')
        
        # Check if token is revoked (extra safety, though we delete on logout)
        if db_token.is_revoked:
            raise AuthenticationFailed('Token has been revoked')
        
        # Check if token is expired (extra safety beyond JWT expiry check)
        if db_token.is_expired():
            raise AuthenticationFailed('Token has expired')
        
        return self.get_user(validated_token), validated_token
