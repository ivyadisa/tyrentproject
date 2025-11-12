from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    path('tenant/', views.tenant_dashboard, name='tenant_dashboard'),
    path('landlord/', views.landlord_dashboard, name='landlord_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('landlord/setup/', views.landlord_setup, name='landlord_setup'),
    path('landlord/upload-house/', views.upload_house, name='upload_house'),
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
]
