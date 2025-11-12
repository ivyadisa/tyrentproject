from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:apartment_id>/', views.book_apartment, name='book_apartment'),
    path('my-bookings/', views.booking_list, name='booking_list'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
