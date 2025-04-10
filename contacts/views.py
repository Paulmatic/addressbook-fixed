from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib import messages
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
                Q(address__icontains=query) |
                Q(file_number__icontains=query) |
                Q(company__icontains=query)
            ).order_by('-rank', 'last_name', 'first_name')
        
        return queryset

class ContactCreateView(CreateView):
    model = Contact
    fields = '__all__'
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contact-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Contact.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle linked clients after main object is saved
        linked_clients = form.cleaned_data.get('linked_clients', [])
        try:
            self.object.linked_clients.set(linked_clients)
        except Exception as e:
            messages.error(self.request, f"Error linking clients: {str(e)}")
            return redirect('contact-create')
        
        return response

class ContactUpdateView(UpdateView):
    model = Contact
    fields = '__all__'
    template_name = 'contacts/contact_form.html'
    success_url = reverse_lazy('contact-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Contact.objects.exclude(id=self.object.id)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle linked clients after main object is saved
        linked_clients = form.cleaned_data.get('linked_clients', [])
        try:
            self.object.linked_clients.set(linked_clients)
        except Exception as e:
            messages.error(self.request, f"Error updating linked clients: {str(e)}")
            return redirect('contact-update', pk=self.object.id)
        
        return response