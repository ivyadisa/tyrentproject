from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.http import JsonResponse
from .models import Property, Apartment
from .forms import PropertyForm, ApartmentForm

# ---------- HOME VIEW ----------
def home(request):
    """Homepage with featured properties, stats, and search."""
    total_properties = Property.objects.count()
    total_units = Apartment.objects.count()
    occupied_units = Apartment.objects.filter(status='Occupied').count()
    vacant_units = total_units - occupied_units

    occupancy_rate = round((occupied_units / total_units) * 100, 1) if total_units > 0 else 0
    vacancy_rate = 100 - occupancy_rate if total_units > 0 else 0

    # Show some featured properties on home page
    properties = Property.objects.all()[:6]

    context = {
        'total_properties': total_properties,
        'total_units': total_units,
        'occupancy_rate': occupancy_rate,
        'vacancy_rate': vacancy_rate,
        'properties': properties,
    }
    return render(request, 'home.html', context)

# ---------- PROPERTY VIEWS ----------
def property_list(request):
    """Show all properties or search results (public)."""
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')
    max_price = request.GET.get('max_price', '')

    properties = Property.objects.all()
    if location:
        properties = properties.filter(address__icontains=location)
    if property_type:
        properties = properties.filter(property_type__icontains=property_type)
    if max_price:
        properties = properties.filter(apartments__rent__lte=max_price)

    properties = properties.distinct()

    return render(request, 'listings/property_list.html', {'properties': properties})

def property_detail(request, pk):
    """Show a single property and its apartments (public)."""
    property = get_object_or_404(Property, pk=pk)
    apartments = property.apartments.all()
    return render(request, 'listings/property_detail.html', {'property': property, 'apartments': apartments})

# ---------- PROTECTED VIEWS (ONLY FOR LOGGED-IN USERS) ----------
from django.contrib.auth.decorators import login_required

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'listings/property_form.html', {'form': form, 'model_name': 'Property', 'is_edit': False})

@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            return redirect('property_detail', pk=property.pk)
    else:
        form = PropertyForm(instance=property)
    return render(request, 'listings/property_form.html', {'form': form, 'model_name': 'Property', 'is_edit': True})

@login_required
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    return redirect('property_list')

# Apartment views remain login required
@login_required
def add_apartment(request, property_pk):
    property = get_object_or_404(Property, pk=property_pk)
    if request.method == 'POST':
        form = ApartmentForm(request.POST)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.property = property
            apartment.save()
            return redirect('property_detail', pk=property.pk)
    else:
        form = ApartmentForm()
    return render(request, 'listings/apartment_form.html', {'form': form, 'property': property, 'model_name': 'Apartment', 'is_edit': False})

@login_required
def edit_apartment(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    if request.method == 'POST':
        form = ApartmentForm(request.POST, instance=apartment)
        if form.is_valid():
            form.save()
            return redirect('property_detail', pk=apartment.property.pk)
    else:
        form = ApartmentForm(instance=apartment)
    return render(request, 'listings/apartment_form.html', {'form': form, 'property': apartment.property, 'model_name': 'Apartment', 'is_edit': True})

@login_required
def update_apartment_status(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        tenant_name = request.POST.get('tenant_name')
        apartment.status = 'Occupied' if status == 'Occupied' else 'Vacant'
        apartment.tenant_name = tenant_name if status == 'Occupied' else ''
        apartment.save()
        return redirect('property_detail', pk=apartment.property.pk)
    return render(request, 'listings/update_apartment_status.html', {'apartment': apartment})

def search_properties(request):
    """AJAX search for properties."""
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')
    max_price = request.GET.get('max_price', '')

    properties = Property.objects.all()
    if location:
        properties = properties.filter(address__icontains=location)
    if property_type:
        properties = properties.filter(property_type__icontains=property_type)
    if max_price:
        properties = properties.filter(apartments__rent__lte=max_price)

    properties = properties.distinct()
    results = [{
        'id': p.id,
        'title': p.title,
        'location': p.address,
        'main_image': p.main_image.url if p.main_image else '',
        'average_rent': p.apartments.aggregate(Avg('rent'))['rent__avg'] or 0,
    } for p in properties]

    return JsonResponse({'results': results})

