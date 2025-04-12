from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    ContactViewSet,
    ContactSearchView,
    api_root
)

# Register the ContactViewSet with the router
router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')

# Define API-specific routes
urlpatterns = [
    # API entry point
    path('', api_root, name='api-root'),
    
    # Automatically generated routes for ContactViewSet (e.g., list, create, retrieve)
    path('', include(router.urls)),

    # Token-based authentication endpoint
    path('auth/', obtain_auth_token, name='api-token-auth'),

    # Custom search endpoint
    path('search/', ContactSearchView.as_view(), name='contact-search'),

    # DRF’s built-in login/logout views (browsable API support)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Additional routes like /contacts/relationship-report/ are handled by the ViewSet
]
