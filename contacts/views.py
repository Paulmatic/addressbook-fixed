from django.views.generic import ListView
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q
from .models import Contact

class ContactSearchView(ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    paginate_by = 20
    context_object_name = 'contacts'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        
        if query:
            search_query = SearchQuery(query)
            queryset = queryset.annotate(
                rank=SearchRank('search_vector', search_query)
            ).filter(
                Q(search_vector=search_query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query)
            ).order_by('-rank', 'last_name', 'first_name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
