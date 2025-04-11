from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
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
                Q(file_number__icontains=search_query)
            ).order_by('-rank', 'last_name', 'first_name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

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

class ClientLinkReportView(TemplateView):
    template_name = 'contacts/client_link_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['top_files'] = Contact.objects.annotate(
            client_count=Count('linked_clients')
        ).filter(client_count__gt=0).order_by('-client_count')
        
        context['top_clients'] = Contact.objects.annotate(
            file_count=Count('linked_contacts')
        ).filter(file_count__gt=0).order_by('-file_count')
        
        return context