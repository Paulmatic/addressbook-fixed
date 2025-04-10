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
            'id', 'file_number', 'first_name', 'middle_name', 'last_name',
            'file_status', 'client_status', 'company', 'linked_clients',
            'email', 'phone_number', 'address', 'created_at'
        ]
        read_only_fields = ('created_at',)