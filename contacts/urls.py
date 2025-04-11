from django.urls import path
from .views import (
    ContactSearchView, 
    ContactCreateView, 
    ContactUpdateView,
    ClientLinkReportView,  # Add the new report view
    contact_detail_view    # Add a detail view if needed
)

urlpatterns = [
    # Existing URLs
    path('', ContactSearchView.as_view(), name='contact-list'),
    path('add/', ContactCreateView.as_view(), name='contact-add'),
    path('<int:pk>/edit/', ContactUpdateView.as_view(), name='contact-edit'),
    
    # New URLs for relationship reporting
    path('reports/relationships/', ClientLinkReportView.as_view(), name='client-link-report'),
    path('<int:pk>/', contact_detail_view, name='contact-detail'),  # Example detail view
]