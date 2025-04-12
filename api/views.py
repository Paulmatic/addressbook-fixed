from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q, Count, Prefetch
from contacts.models import Contact
from .serializers import ContactSerializer
from .permissions import IsOwnerOrReadOnly

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint that provides hyperlinks to all API endpoints
    """
    return Response({
        'contacts': reverse('contact-list', request=request, format=format),
        'contact-search': reverse('contact-search', request=request, format=format),
        'token-auth': reverse('api-token-auth', request=request, format=format),
        'relationship-report': reverse('contact-relationship-report', request=request, format=format),
        'api-auth': reverse('rest_framework:login', request=request, format=format),
    })

class ContactSearchView(ListAPIView):
    """
    Dedicated search endpoint for contacts
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Contact.objects.all()
        search_query = self.request.query_params.get('q', '').strip()
        
        if search_query:
            queryset = queryset.annotate(
                rank=SearchRank('search_vector', SearchQuery(search_query))
            ).filter(
                Q(search_vector=SearchQuery(search_query)) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(file_number__icontains=search_query) |
                Q(email__icontains=search_query)
            ).order_by('-rank', 'last_name', 'first_name')
        
        return queryset

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('last_name', 'first_name')
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """
        Optimized queryset with search functionality and prefetching
        """
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        
        # Prefetch related data to avoid N+1 queries
        queryset = queryset.prefetch_related(
            Prefetch('linked_clients', queryset=Contact.objects.only('id', 'first_name', 'last_name', 'file_number')),
            Prefetch('linked_contacts', queryset=Contact.objects.only('id', 'first_name', 'last_name', 'file_number'))
        )
        
        if search_query:
            queryset = queryset.annotate(
                rank=SearchRank('search_vector', SearchQuery(search_query))
            ).filter(
                Q(search_vector=SearchQuery(search_query)) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(file_number__icontains=search_query) |
                Q(email__icontains=search_query)
            ).order_by('-rank', 'last_name', 'first_name')
            
        return queryset
    
    @action(detail=True, methods=['get'], url_path='linked-clients', url_name='linked-clients')
    def linked_clients(self, request, pk=None):
        """
        Get all clients linked to this contact (file)
        """
        contact = self.get_object()
        page = self.paginate_queryset(contact.linked_clients.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(contact.linked_clients.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='linked-files', url_name='linked-files')
    def linked_files(self, request, pk=None):
        """
        Get all files linked to this contact (client)
        """
        contact = self.get_object()
        page = self.paginate_queryset(contact.linked_contacts.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(contact.linked_contacts.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='relationship-report', url_name='contact-relationship-report')
    def relationship_report(self, request):
        """
        Enhanced relationship report with statistics and serialized data
        """
        queryset = self.get_queryset()
        
        top_files = queryset.annotate(
            client_count=Count('linked_clients')
        ).filter(client_count__gt=0).order_by('-client_count')[:10]
        
        top_clients = queryset.annotate(
            file_count=Count('linked_contacts')
        ).filter(file_count__gt=0).order_by('-file_count')[:10]
        
        data = {
            'top_files': ContactSerializer(top_files, many=True).data,
            'top_clients': ContactSerializer(top_clients, many=True).data,
            'stats': {
                'total_contacts': Contact.objects.count(),
                'linked_contacts': Contact.objects.filter(linked_clients__isnull=False).count(),
                'unlinked_contacts': Contact.objects.filter(linked_clients__isnull=True).count(),
                'contacts_with_links': Contact.objects.filter(
                    Q(linked_clients__isnull=False) | 
                    Q(linked_contacts__isnull=False)
                ).distinct().count()
            }
        }
        return Response(data, status=status.HTTP_200_OK)
    
    def perform_create(self, serializer):
        """Set the owner to the current user on creation"""
        serializer.save(owner=self.request.user)