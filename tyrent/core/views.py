# core/views.py and accounts/views.py combined
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from listings.models import Property, Apartment
from django.db.models import Avg
from accounts.models import LandlordProfile

# ====================== CORE VIEWS ======================

def home(request):
    # ---------- CONTACT FORM ----------
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            try:
                send_mail(
                    subject=f"Contact Form Submission from {name}",
                    message=message,
                    from_email=email,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception:
                messages.error(request, "Error sending message. Please try again later.")

    # ---------- PROPERTY STATS ----------
    total_properties = Property.objects.count()
    total_units = Apartment.objects.count()
    occupied_units = Apartment.objects.filter(status='Occupied').count()
    vacant_units = total_units - occupied_units

    occupancy_rate = round((occupied_units / total_units) * 100, 1) if total_units > 0 else 0
    vacancy_rate = 100 - occupancy_rate if total_units > 0 else 0

    # ---------- FEATURED PROPERTIES ----------
    featured_properties = Property.objects.all()[:6]
    properties_with_avg_rent = []
    for p in featured_properties:
        avg_rent = p.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0
        p.avg_rent = avg_rent
        properties_with_avg_rent.append(p)

    # ---------- VACANT APARTMENTS ----------
    vacant_apartments = Apartment.objects.filter(status='Vacant').order_by('-id')  # all vacant apartments

    context = {
        'total_properties': total_properties,
        'total_units': total_units,
        'occupancy_rate': occupancy_rate,
        'vacancy_rate': vacancy_rate,
        'properties': properties_with_avg_rent,
        'vacant_apartments': vacant_apartments,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


# ====================== ACCOUNTS VIEWS ======================

@login_required
@login_required
def landlord_dashboard(request):
    # Ensure the user is a landlord
    if request.user.role != "LANDLORD":
        return redirect("home")  # Redirect non-landlords to home

    # Optional: get the LandlordProfile for display purposes
    try:
        landlord_profile = request.user.landlord_profile
    except LandlordProfile.DoesNotExist:
        messages.error(request, "Landlord profile not found.")
        return redirect("home")

    # Use request.user for queries since Property.landlord is a User FK
    properties = Property.objects.filter(landlord=request.user)

    vacant_apartments = Apartment.objects.filter(
        property__landlord=request.user,
        status='Vacant'
    ).order_by('-id')

    # Calculate total and vacant units per property
    properties_data = []
    for prop in properties:
        total_units = prop.apartments.count()
        vacant_units = prop.apartments.filter(status='Vacant').count()
        properties_data.append({
            'property': prop,
            'total_units': total_units,
            'vacant_units': vacant_units,
        })

    context = {
        'properties': properties_data,
        'vacant_apartments': vacant_apartments,
        'landlord_profile': landlord_profile,  # optional, for template
    }

    return render(request, 'accounts/landlord_dashboard.html', context)
