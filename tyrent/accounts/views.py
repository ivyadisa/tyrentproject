from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import CustomAuthenticationForm
from .models import User, LandlordProfile, TenantProfile
from listings.models import Property, Apartment
from listings.forms import PropertyForm, ApartmentForm, VacantHouseForm
from bookings.models import Booking


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        full_name = request.POST['full_name']
        phone_number = request.POST.get('phone_number')
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST['role']

        if password1 != password2:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        user = User.objects.create_user(
            username=username,
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            password=password1,
            role=role
        )

        if role == 'LANDLORD':
            LandlordProfile.objects.create(user=user)
        elif role == 'TENANT':
            TenantProfile.objects.create(user=user)

        login(request, user)

        if role == 'LANDLORD':
            return redirect('landlord_setup')
        else:
            return redirect('tenant_dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'TENANT':
                return redirect('tenant_dashboard')
            elif user.role == 'LANDLORD':
                return redirect('landlord_dashboard')
            else:
                return redirect('admin_dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def tenant_dashboard(request):
    if request.user.role != "TENANT":
        return redirect('home')

    tenant_profile = request.user.tenant_profile
    bookings = Booking.objects.filter(tenant=request.user).order_by('-created_at')

    context = {
        'tenant': tenant_profile,
        'bookings': bookings
    }
    return render(request, 'accounts/tenant_dashboard.html', context)


@login_required
def landlord_setup(request):
    if request.user.role != 'LANDLORD':
        return redirect('home')

    try:
        landlord_profile = request.user.landlord_profile
        return redirect('landlord_dashboard')
    except LandlordProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        LandlordProfile.objects.create(
            user=request.user,
            property_name=request.POST.get('property_name'),
            company_name=request.POST.get('company_name'),
            business_permit_number=request.POST.get('business_permit_number'),
            address=request.POST.get('address')
        )
        return redirect('landlord_dashboard')

    return render(request, 'accounts/landlord_setup.html')


@login_required
def landlord_dashboard(request):
    if request.user.role != 'LANDLORD':
        return redirect('home')

    landlord_user = request.user
    properties = Property.objects.filter(landlord=landlord_user)
    apartments = Apartment.objects.filter(property__in=properties)

    property_form = PropertyForm()
    apartment_form = ApartmentForm()

    if request.method == "POST":
        # ---------------- Add Property ----------------
        if 'property_submit' in request.POST:
            property_form = PropertyForm(request.POST, request.FILES)
            if property_form.is_valid():
                new_property = property_form.save(commit=False)
                new_property.landlord = landlord_user
                new_property.save()
                messages.success(request, "Property added successfully!")
                return redirect('landlord_dashboard')
            else:
                messages.error(request, "Please fill all fields correctly for the property.")

        # ---------------- Add Apartment ----------------
        elif 'apartment_submit' in request.POST:
            apartment_form = ApartmentForm(request.POST, request.FILES)
            if apartment_form.is_valid():
                new_apartment = apartment_form.save(commit=False)
                
                # Assign property if not selected
                if not new_apartment.property_id:
                    first_property = properties.first()
                    if first_property:
                        new_apartment.property = first_property
                    else:
                        messages.error(request, "You need to add a property first.")
                        return redirect('landlord_dashboard')

                new_apartment.save()
                messages.success(request, "Apartment added successfully!")
                return redirect('landlord_dashboard')
            else:
                messages.error(request, "Please fill all fields correctly for the apartment.")

    context = {
        'landlord': request.user.landlord_profile,
        'properties': properties,
        'apartments': apartments,
        'property_form': property_form,
        'apartment_form': apartment_form,
    }
    return render(request, 'accounts/landlord_dashboard.html', context)


@login_required
def upload_house(request):
    landlord = request.user.landlord_profile
    if request.method == "POST":
        form = VacantHouseForm(request.POST, request.FILES)
        if form.is_valid():
            apartment = form.save(commit=False)
            property_instance = Property.objects.filter(landlord=landlord).first()
            if not property_instance:
                messages.error(request, "You need to create a property first.")
                return redirect('landlord_dashboard')
            apartment.property = property_instance
            apartment.status = 'Vacant'
            apartment.save()
            messages.success(request, "Apartment uploaded successfully!")
        else:
            messages.error(request, "Please fill all fields and upload image/video correctly.")
    return redirect('landlord_dashboard')


def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")
