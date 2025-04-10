from django.urls import path
from .views import ContactSearchView

urlpatterns = [
    path('', ContactSearchView.as_view(), name='contact-list'),
]

