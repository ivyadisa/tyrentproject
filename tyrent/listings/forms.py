from django import forms
from .models import Property, Apartment

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'address', 'main_image']

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['title', 'unit_number', 'bedrooms', 'rent', 'location', 'status', 'tenant_name', 'notes', 'image', 'video']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class VacantHouseForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['property', 'title', 'description', 'rent', 'image', 'video']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
