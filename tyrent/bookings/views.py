from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Apartment
from .models import Booking
from .forms import BookingForm

@login_required
def book_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    
    if request.user.role == "LANDLORD" and request.user == apartment.landlord.user:
        messages.warning(request, "You cannot book your own apartment.")
        return redirect('property_detail', pk=apartment.property.id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tenant = request.user
            booking.apartment = apartment
            booking.save()
            messages.success(request, "Your booking request has been submitted!")
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'bookings/book_apartment.html', {'form': form, 'apartment': apartment})


@login_required
def booking_list(request):
    """
    Display all bookings for the logged-in tenant or landlord.
    Landlord sees bookings for their apartments.
    Tenant sees only their own bookings.
    """
    if request.user.role == "LANDLORD":
        bookings = Booking.objects.filter(apartment__landlord__user=request.user)
    else:
        bookings = Booking.objects.filter(tenant=request.user)

    return render(request, 'bookings/booking_list.html', {'bookings': bookings})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.role == "TENANT" and booking.tenant != request.user:
        messages.error(request, "You do not have permission to view this booking.")
        return redirect('booking_list')

    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.role == "TENANT" and booking.tenant != request.user:
        messages.error(request, "You do not have permission to view this confirmation.")
        return redirect('booking_list')

    return render(request, 'bookings/booking_confirmation.html', {'booking': booking})
