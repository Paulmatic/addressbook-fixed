from django.urls import path
from .views import (
    ContactListView,
    ContactDetailView,
    ContactCreateView,
    ContactUpdateView,
    ContactDeleteView,
    ContactSearchView,
    ClientLinkReportView
)

urlpatterns = [
    path('', ContactListView.as_view(), name='contact-list'),
    path('search/', ContactSearchView.as_view(), name='contact-search'),
    path('<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('add/', ContactCreateView.as_view(), name='contact-add'),
    path('<int:pk>/edit/', ContactUpdateView.as_view(), name='contact-edit'),
    path('<int:pk>/delete/', ContactDeleteView.as_view(), name='contact-delete'),
    path('reports/links/', ClientLinkReportView.as_view(), name='client-link-report'),
]