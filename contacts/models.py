from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinLengthValidator, EmailValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Contact(models.Model):
    class FileStatus(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')

    class ClientStatus(models.TextChoices):
        ALIVE = 'ALIVE', _('Alive')
        DECEASED = 'DECEASED', _('Deceased')

    # Personal Information
    first_name = models.CharField(
        _('first name'),
        max_length=50,
        db_index=True,
        validators=[MinLengthValidator(2)]
    )
    middle_name = models.CharField(
        _('middle name'),
        max_length=50,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=50,
        db_index=True,
        validators=[MinLengthValidator(2)]
    )
    
    # Contact Information
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        db_index=True,
        unique=True
    )
    email = models.EmailField(
        _('email'),
        db_index=True,
        unique=True,
        validators=[EmailValidator()]
    )
    address = models.TextField(
        _('address'),
        db_index=True
    )
    
    # File Management
    file_status = models.CharField(
        _('file status'),
        max_length=6,
        choices=FileStatus.choices,
        default=FileStatus.OPEN,
        db_index=True
    )
    file_number = models.CharField(
        _('file number'),
        max_length=20,
        unique=True,
        db_index=True
    )
    
    # Client Status
    client_status = models.CharField(
        _('client status'),
        max_length=8,
        choices=ClientStatus.choices,
        default=ClientStatus.ALIVE,
        db_index=True
    )
    
    # Relationships
    company = models.CharField(
        _('company'),
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )
    linked_clients = models.ManyToManyField(
        'self',
        verbose_name=_('linked clients'),
        blank=True,
        symmetrical=False,
        related_name='linked_contacts'
    )
    
    # Metadata
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    search_vector = SearchVectorField(
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        ordering = ['last_name', 'first_name']
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['file_number']),
            models.Index(fields=['client_status']),
            models.Index(fields=['file_status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.file_number})"
    
    def get_absolute_url(self):
        return reverse('contact-detail', kwargs={'pk': self.pk})
    
    def get_linked_clients(self):
        """Returns queryset of linked clients"""
        return self.linked_clients.all()
    
    def get_linked_files(self):
        """Returns queryset of files this client is linked to"""
        return self.linked_contacts.all()
    
    def save(self, *args, **kwargs):
        # Data cleaning
        self.email = self.email.lower().strip()
        self.phone_number = ''.join(c for c in self.phone_number if c.isdigit() or c == '+')
        super().save(*args, **kwargs)