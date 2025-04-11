from rest_framework import serializers
from contacts.models import Contact

class ContactSerializer(serializers.ModelSerializer):
    linked_clients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Contact.objects.all(),
        required=False
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
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']