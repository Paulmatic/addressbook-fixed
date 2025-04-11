from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from contacts.models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('last_name', 'first_name')
    serializer_class = ContactSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(search_vector=SearchQuery(search_query)) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(file_number__icontains=search_query)
            )
        return queryset
    
    @action(detail=True, methods=['get'])
    def linked_clients(self, request, pk=None):
        contact = self.get_object()
        serializer = self.get_serializer(
            contact.linked_clients.all(),
            many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def linked_files(self, request, pk=None):
        contact = self.get_object()
        serializer = self.get_serializer(
            contact.linked_contacts.all(),
            many=True
        )
        return Response(serializer.data)