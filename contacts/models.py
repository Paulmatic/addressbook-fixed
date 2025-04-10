from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class Contact(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=50, db_index=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)  # New
    last_name = models.CharField(max_length=50, db_index=True)
    
    # Contact Information (existing)
    phone_number = models.CharField(max_length=15, db_index=True)
    email = models.EmailField(db_index=True)
    address = models.TextField(db_index=True)
    
    # File Management (new)
    FILE_STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    file_status = models.CharField(
        max_length=6,
        choices=FILE_STATUS_CHOICES,
        default='OPEN',
        db_index=True
    )
    file_number = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Client Status (new)
    CLIENT_STATUS_CHOICES = [
        ('ALIVE', 'Alive'),
        ('DECEASED', 'Deceased'),
    ]
    client_status = models.CharField(
        max_length=8,
        choices=CLIENT_STATUS_CHOICES,
        default='ALIVE',
        db_index=True
    )
    
    # Relationships (new)
    company = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    linked_clients = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Linked Clients'
    )
    
    # Metadata (existing)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            GinIndex(fields=['first_name', 'last_name']),
            GinIndex(fields=['file_number']),  # New index
        ]
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.file_number})"  # Updated
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.db import transaction
        transaction.on_commit(lambda: self.update_search_vector())
    
    def update_search_vector(self):
        from django.contrib.postgres.search import SearchVector
        Contact.objects.filter(pk=self.pk).update(
            search_vector=SearchVector(
                'first_name', 'last_name', 'email', 
                'address', 'phone_number', 'file_number',  # Added file_number to search
                'company'  # Added company to search
            )
        )