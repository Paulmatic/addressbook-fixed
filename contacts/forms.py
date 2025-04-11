from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'linked_clients': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['file_number'].required = True
        
        # If editing an existing contact, exclude it from linked clients
        if self.instance and self.instance.pk:
            self.fields['linked_clients'].queryset = Contact.objects.exclude(pk=self.instance.pk)