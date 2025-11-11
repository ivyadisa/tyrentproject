from django import forms
from .models import Property, Apartment

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        # Removed 'status' because Property no longer has this field
        fields = ['title', 'description', 'property_type', 'address', 'main_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['unit_number', 'status', 'rent', 'tenant_name', 'notes']  # Keep status here
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
