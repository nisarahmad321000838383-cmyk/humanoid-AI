"""
Custom JWT Authentication that reads tokens from HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads the access token from cookies
    instead of the Authorization header.
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
        
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
