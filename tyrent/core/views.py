# core/views.py
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from listings.models import Property, Apartment
from django.db.models import Avg

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
            except Exception as e:
                messages.error(request, "Error sending message. Please try again later.")

    # ---------- PROPERTY STATS ----------
    total_properties = Property.objects.count()
    total_units = Apartment.objects.count()
    occupied_units = Apartment.objects.filter(status='Occupied').count()
    vacant_units = total_units - occupied_units

    occupancy_rate = round((occupied_units / total_units) * 100, 1) if total_units > 0 else 0
    vacancy_rate = 100 - occupancy_rate if total_units > 0 else 0

    # Featured properties (first 6)
    featured_properties = Property.objects.all()[:6]

    # Compute average rent for each property
    properties_with_avg_rent = []
    for p in featured_properties:
        avg_rent = p.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0
        p.avg_rent = avg_rent
        properties_with_avg_rent.append(p)

    context = {
        'total_properties': total_properties,
        'total_units': total_units,
        'occupancy_rate': occupancy_rate,
        'vacancy_rate': vacancy_rate,
        'properties': properties_with_avg_rent,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')
