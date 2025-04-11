from rest_framework import serializers
from contacts.models import Contact

class ContactSerializer(serializers.ModelSerializer):
    linked_clients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Contact.objects.all(),
        required=False,
        help_text="List of IDs of linked client contacts"
    )
    
    # Add these fields to show client details instead of just IDs
    linked_clients_details = serializers.SerializerMethodField(
        read_only=True,
        help_text="Detailed information about linked clients"
    )
    
    linked_files_count = serializers.IntegerField(
        read_only=True,
        help_text="Count of files this client is linked to"
    )

    class Meta:
        model = Contact
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'phone_number',
            'email',
            'address',
            'file_status',
            'file_number',
            'client_status',
            'company',
            'linked_clients',
            'linked_clients_details',
            'linked_files_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'linked_clients_details', 'linked_files_count']
        extra_kwargs = {
            'file_number': {'required': True},
            'email': {'validators': []}  # Disable unique validation for updates
        }

    def get_linked_clients_details(self, obj):
        """Return nested details of linked clients"""
        from .serializers import ContactSerializer  # Avoid circular import
        return ContactSerializer(
            obj.linked_clients.all(),
            many=True,
            context=self.context
        ).data

    def validate(self, data):
        """Custom validation for contact relationships"""
        instance = self.instance
        linked_clients = data.get('linked_clients', [])
        
        # Prevent linking to self
        if instance and instance in linked_clients:
            raise serializers.ValidationError({
                'linked_clients': "A contact cannot be linked to itself"
            })
        
        # Validate file number uniqueness on creation
        if not instance and Contact.objects.filter(file_number=data.get('file_number')).exists():
            raise serializers.ValidationError({
                'file_number': "This file number already exists"
            })
            
        return data

    def create(self, validated_data):
        """Handle creation with many-to-many relationships"""
        linked_clients = validated_data.pop('linked_clients', [])
        contact = Contact.objects.create(**validated_data)
        contact.linked_clients.set(linked_clients)
        return contact

    def update(self, instance, validated_data):
        """Handle update with many-to-many relationships"""
        linked_clients = validated_data.pop('linked_clients', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update relationships if provided
        if linked_clients is not None:
            instance.linked_clients.set(linked_clients)
            
        return instance