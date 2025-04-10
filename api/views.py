from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django.contrib.postgres.search import SearchQuery
from contacts.models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        'first_name', 'last_name', 'email', 
        'phone_number', 'address', 'file_number',
        'company'
    ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('search', None)
        
        if query:
            return queryset.filter(search_vector=SearchQuery(query))
        return queryset