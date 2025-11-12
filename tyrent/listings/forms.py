from django import forms
from .models import Property, Apartment

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'address', 'main_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['unit_number', 'location', 'bedrooms', 'rent', 'status', 'tenant_name', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
