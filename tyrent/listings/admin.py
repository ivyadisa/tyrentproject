from django.contrib import admin
from .models import Property, Apartment

# ---------- Property Admin ----------
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'address', 'date_added')  # Removed 'status'
    list_filter = ('property_type', 'date_added')  # Removed 'status'
    search_fields = ('title', 'address', 'description')

# ---------- Apartment Admin ----------
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('property', 'unit_number', 'status', 'rent', 'tenant_name', 'date_added')
    list_filter = ('status', 'property')
    search_fields = ('unit_number', 'tenant_name', 'property__title')

admin.site.register(Property, PropertyAdmin)
admin.site.register(Apartment, ApartmentAdmin)
