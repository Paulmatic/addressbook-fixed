from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinLengthValidator, EmailValidator

class Contact(models.Model):
    # Personal Information
    first_name = models.CharField(
        max_length=50,
        db_index=True,  # Regular B-tree index
        validators=[MinLengthValidator(2)]
    )
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Optional middle name"
    )
    last_name = models.CharField(
        max_length=50,
        db_index=True,  # Regular B-tree index
        validators=[MinLengthValidator(2)]
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=15,
        db_index=True,  # Regular B-tree index
        unique=True,
        help_text="Format: +1234567890"
    )
    email = models.EmailField(
        db_index=True,  # Regular B-tree index
        unique=True,
        validators=[EmailValidator()],
        help_text="Valid email address required"
    )
    address = models.TextField(
        db_index=True,  # Regular B-tree index
        help_text="Full postal address"
    )
    
    # File Management
    FILE_STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]
    file_status = models.CharField(
        max_length=6,
        choices=FILE_STATUS_CHOICES,
        default='OPEN',
        db_index=True,  # Regular B-tree index
        help_text="Current file status"
    )
    file_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,  # Regular B-tree index
        help_text="Unique file identifier"
    )
    
    # Client Status
    CLIENT_STATUS_CHOICES = [
        ('ALIVE', 'Alive'),
        ('DECEASED', 'Deceased'),
    ]
    client_status = models.CharField(
        max_length=8,
        choices=CLIENT_STATUS_CHOICES,
        default='ALIVE',
        db_index=True,  # Regular B-tree index
        help_text="Current client status"
    )
    
    # Relationships
    company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,  # Regular B-tree index
        help_text="Associated company if applicable"
    )
    linked_clients = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='linked_contacts',
        verbose_name='Linked Clients',
        help_text="Other contacts related to this one"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        indexes = [
            # GIN index only for search_vector
            GinIndex(fields=['search_vector']),
            
            # Regular B-tree indexes for other fields
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['file_number']),
            models.Index(fields=['last_name', 'first_name']),
            
            # For advanced name search (requires pg_trgm extension)
            # GinIndex(
            #     fields=['first_name', 'last_name'],
            #     name='contact_name_gin_trgm_idx',
            #     opclasses=['gin_trgm_ops', 'gin_trgm_ops']
            # ),
        ]
        ordering = ['last_name', 'first_name']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return f"{name} ({self.file_number})"
    
    def save(self, *args, **kwargs):
        # Clean data before saving
        self.email = self.email.lower().strip()
        self.phone_number = ''.join(c for c in self.phone_number if c.isdigit() or c == '+')
        super().save(*args, **kwargs)
        
        # Update search vector after commit
        from django.db import transaction
        transaction.on_commit(lambda: self.update_search_vector())
    
    def update_search_vector(self):
        from django.contrib.postgres.search import SearchVector
        Contact.objects.filter(pk=self.pk).update(
            search_vector=SearchVector(
                'first_name', 'last_name', 'email',
                'address', 'phone_number', 'file_number',
                'company'
            )
        )
    
    @property
    def full_name(self):
        """Return the full name of the contact."""
        names = [n for n in [self.first_name, self.middle_name, self.last_name] if n]
        return ' '.join(names)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('contact-detail', kwargs={'pk': self.pk})