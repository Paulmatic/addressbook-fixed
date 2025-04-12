from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from .forms import ContactForm

class ContactListView(ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '').strip()
        
        if search_query:
            queryset = queryset.annotate(
                rank=SearchRank('search_vector', SearchQuery(search_query))
            ).filter(
                Q(search_vector=SearchQuery(search_query)) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(file_number__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            ).order_by('-rank', 'last_name', 'first_name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ContactDetailView(DetailView):
    model = Contact
    template_name = 'contacts/contact_detail.html'
    context_object_name = 'contact'

class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contact-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Contact '{self.object}' was created successfully."
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct the errors below."
        )
        return super().form_invalid(form)

class ContactUpdateView(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/contact_form.html'
    
    def get_success_url(self):
        return reverse_lazy('contact-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Contact '{self.object}' was updated successfully."
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct the errors below."
        )
        return super().form_invalid(form)

class ContactDeleteView(DeleteView):
    model = Contact
    template_name = 'contacts/contact_confirm_delete.html'
    success_url = reverse_lazy('contact-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f"Contact '{self.object}' was deleted successfully."
        )
        return response

class ContactSearchView(ListView):
    model = Contact
    template_name = 'contacts/contact_search.html'
    context_object_name = 'contacts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '').strip()
        
        if search_query:
            vector = SearchVector('first_name', 'last_name', 'email', 'phone_number', 'file_number')
            queryset = queryset.annotate(
                search=vector,
                rank=SearchRank(vector, SearchQuery(search_query))
            ).filter(
                Q(search=SearchQuery(search_query)) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(file_number__icontains=search_query)
            ).order_by('-rank')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ClientLinkReportView(TemplateView):
    template_name = 'contacts/client_link_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['top_files'] = Contact.objects.annotate(
            client_count=Count('linked_clients')
        ).filter(client_count__gt=0).order_by('-client_count')[:10]
        
        context['top_clients'] = Contact.objects.annotate(
            file_count=Count('linked_contacts')
        ).filter(file_count__gt=0).order_by('-file_count')[:10]
        
        context['unlinked_contacts'] = Contact.objects.filter(
            linked_clients__isnull=True
        ).count()
        
        context['total_contacts'] = Contact.objects.count()
        context['linked_contacts'] = context['total_contacts'] - context['unlinked_contacts']
        
        return context

class ClientRelationshipReportView(APIView):
    """
    API endpoint that provides client relationship statistics
    """
    def get(self, request, format=None):
        top_files = Contact.objects.annotate(
            client_count=Count('linked_clients')
        ).filter(client_count__gt=0).order_by('-client_count')[:10]
        
        top_clients = Contact.objects.annotate(
            file_count=Count('linked_contacts')
        ).filter(file_count__gt=0).order_by('-file_count')[:10]
        
        data = {
            'top_files': [
                {
                    'id': contact.id,
                    'file_number': contact.file_number,
                    'name': f"{contact.first_name} {contact.last_name}",
                    'client_count': contact.client_count
                } for contact in top_files
            ],
            'top_clients': [
                {
                    'id': contact.id,
                    'name': f"{contact.first_name} {contact.last_name}",
                    'file_count': contact.file_count
                } for contact in top_clients
            ],
            'stats': {
                'total_contacts': Contact.objects.count(),
                'linked_contacts': Contact.objects.filter(linked_clients__isnull=False).count(),
                'unlinked_contacts': Contact.objects.filter(linked_clients__isnull=True).count(),
            }
        }
        return Response(data, status=status.HTTP_200_OK)
    