from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    ContactViewSet,
    ClientRelationshipReportView,
    ContactSearchView,
    api_root
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')

# Additional API endpoints
urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('auth/', obtain_auth_token, name='api-token-auth'),
    path('search/', ContactSearchView.as_view(), name='contact-search'),
    path('reports/relationships/', 
         ClientRelationshipReportView.as_view(), 
         name='client-relationships-report'),
    
    # Include DRF's login/logout for browsable API
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]