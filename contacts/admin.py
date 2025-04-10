from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('file_number', 'first_name', 'last_name', 'file_status', 'client_status')
    list_filter = ('file_status', 'client_status', 'company')
    filter_horizontal = ('linked_clients',)  # For easier many-to-many management

admin.site.register(Contact, ContactAdmin)