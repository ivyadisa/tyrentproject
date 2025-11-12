from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/add/', views.add_property, name='add_property'),
    path('properties/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('properties/<int:pk>/delete/', views.delete_property, name='delete_property'),
    path('properties/<int:property_pk>/add_apartment/', views.add_apartment, name='add_apartment'),
    path('apartments/<int:pk>/edit/', views.edit_apartment, name='edit_apartment'),
    path('apartments/<int:pk>/update_status/', views.update_apartment_status, name='update_apartment_status'),
    path('search/', views.search_properties, name='search_properties'),
    path('apartment/<int:pk>/', views.apartment_detail, name='apartment_detail'),

]
