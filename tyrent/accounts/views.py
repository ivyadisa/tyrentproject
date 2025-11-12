from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import CustomAuthenticationForm
from .models import User, LandlordProfile, TenantProfile
from .models import VacantHouse
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
    tenant_profile = request.user.tenant_profile
    return render(request, 'accounts/tenant_dashboard.html', {'tenant': tenant_profile})


@login_required
def landlord_dashboard(request):
    landlord = request.user.landlord_profile  
    houses = VacantHouse.objects.filter(landlord=landlord)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if title and description and image:
            VacantHouse.objects.create(
                landlord=landlord,
                title=title,
                description=description,
                image=image
            )
            messages.success(request, "House uploaded successfully!")
            return redirect('landlord_dashboard')
        else:
            messages.error(request, "Please fill all fields and upload an image.")

    context = {
        'landlord': landlord,
        'houses': houses
    }
    return render(request, 'accounts/landlord_dashboard.html', context)

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

def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")

@login_required
def upload_house(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        
        VacantHouse.objects.create(
            landlord=request.user.landlord_profile,
            title=title,
            description=description,
            image=image
        )
        return redirect('landlord_dashboard')
    return redirect('landlord_dashboard')

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
