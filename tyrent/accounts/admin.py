from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TenantProfile, LandlordProfile, VacantHouse


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('full_name', 'username', 'email', 'role', 'status', 'verification_status', 'is_staff', 'created_at')
    list_filter = ('role', 'status', 'verification_status', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'full_name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'verification_date')

    fieldsets = (
        ('Login Info', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('full_name', 'phone_number', 'profile_picture_url', 'bio')
        }),
        ('Role & Status', {
            'fields': ('role', 'status')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_notes', 'verification_date', 'verified_by_admin')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'phone_number', 'password1', 'password2', 'role', 'status'),
        }),
    )


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_address', 'preferred_location', 'occupation')
    search_fields = ('user__full_name', 'user__email', 'preferred_location')


@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'property_name', 'company_name', 'business_permit_number', 'national_id')
    search_fields = ('user__full_name', 'company_name', 'business_permit_number')


@admin.register(VacantHouse)
class VacantHouseAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'rent_amount', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('title', 'landlord__user__full_name', 'address')
    readonly_fields = ('created_at', 'updated_at')

