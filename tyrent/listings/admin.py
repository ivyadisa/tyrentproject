from django.contrib import admin
from .models import Property, Apartment

# ---------- Property Admin ----------
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'address', 'date_added')
    list_filter = ('property_type', 'date_added')
    search_fields = ('title', 'address', 'description')

# ---------- Apartment Admin ----------
@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('property', 'unit_number', 'status', 'rent', 'location', 'tenant_name', 'date_added')
    list_filter = ('status', 'property', 'location')
    search_fields = ('unit_number', 'tenant_name', 'property__title', 'location')
    fields = ('property', 'unit_number', 'rent', 'location', 'status', 'tenant_name', 'notes')
