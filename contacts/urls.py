from django.urls import path
from .views import ContactSearchView, ContactCreateView, ContactUpdateView

urlpatterns = [
    path('', ContactSearchView.as_view(), name='contact-list'),
    path('add/', ContactCreateView.as_view(), name='contact-add'),
    path('<int:pk>/edit/', ContactUpdateView.as_view(), name='contact-edit'),
]