from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import custom TokenRefreshView from views instead of simplejwt
from .views import (
    RegisterView, 
    LoginView, 
    CurrentUserView, 
    LogoutView,
    TokenRefreshView,
    ClearCookiesView,
    CheckAvailabilityView,
    HuggingFaceTokenViewSet,
    UserHFTokenAssignmentViewSet
)
from .views_business import (
    BusinessRegisterView,
    BusinessDetailView,
    BusinessSearchView,
    MyBusinessView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'hf-tokens', HuggingFaceTokenViewSet, basename='hf-token')
router.register(r'hf-assignments', UserHFTokenAssignmentViewSet, basename='hf-assignment')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('clear-cookies/', ClearCookiesView.as_view(), name='clear-cookies'),
    path('check-availability/', CheckAvailabilityView.as_view(), name='check-availability'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Business endpoints
    path('business/register/', BusinessRegisterView.as_view(), name='business-register'),
    path('business/my/', MyBusinessView.as_view(), name='my-business'),
    path('business/', BusinessDetailView.as_view(), name='business-detail'),
    path('business/search/', BusinessSearchView.as_view(), name='business-search'),
    path('', include(router.urls)),
]
