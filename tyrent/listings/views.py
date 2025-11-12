from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, Apartment
from .forms import PropertyForm, ApartmentForm

# ---------- HOME VIEW ----------
def home(request):
    """Homepage with featured properties, stats, and search."""

    # Total stats
    total_properties = Property.objects.count()
    total_units = Apartment.objects.count()
    occupied_units = Apartment.objects.filter(status='Occupied').count()
    vacant_units = total_units - occupied_units

    occupancy_rate = round((occupied_units / total_units) * 100, 1) if total_units else 0
    vacancy_rate = 100 - occupancy_rate if total_units else 0

    # Featured properties (first 6)
    properties = Property.objects.all()[:6]

    # Add average rent to each property
    for prop in properties:
        prop.avg_rent = prop.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0
        prop.status = "Vacant" if prop.apartments.filter(status="Vacant").exists() else "Occupied"

    context = {
        'total_properties': total_properties,
        'total_units': total_units,
        'occupancy_rate': occupancy_rate,
        'vacancy_rate': vacancy_rate,
        'properties': properties,
    }
    return render(request, 'core/home.html', context)


# ---------- PROPERTY MANAGEMENT ----------

@login_required
def property_list(request):
    """Show all properties or filtered search results."""
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')
    max_price = request.GET.get('max_price', '')

    properties = Property.objects.all()

    if location:
        properties = properties.filter(address__icontains=location)
    if property_type:
        properties = properties.filter(property_type__iexact=property_type.capitalize())
    if max_price:
        try:
            max_price = float(max_price)
            properties = [p for p in properties if (p.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0) <= max_price]
        except ValueError:
            pass

    # Add avg_rent and status
    for prop in properties:
        prop.avg_rent = prop.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0
        prop.status = "Vacant" if prop.apartments.filter(status="Vacant").exists() else "Occupied"

    return render(request, 'listings/property_list.html', {
        'properties': properties,
        'user': request.user
    })


@login_required
def add_property(request):
    """Landlord adds a new property."""
    landlord = request.user
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = landlord
            property.save()
            messages.success(request, "Property uploaded successfully!")
            return redirect('landlord_dashboard')
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
            messages.success(request, "Property updated successfully!")
            return redirect('property_detail', pk=property.pk)
    else:
        form = PropertyForm(instance=property)
    return render(request, 'listings/property_form.html', {'form': form, 'model_name': 'Property', 'is_edit': True})


@login_required
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    messages.success(request, "Property deleted successfully!")
    return redirect('property_list')


@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    apartments = property.apartments.all()
    property.avg_rent = property.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0
    property.status = "Vacant" if property.apartments.filter(status="Vacant").exists() else "Occupied"
    context = {
        'property': property,
        'apartments': apartments,
    }
    return render(request, 'listings/property_detail.html', context)


# ---------- APARTMENT MANAGEMENT ----------

@login_required
def add_apartment(request, property_pk):
    property = get_object_or_404(Property, pk=property_pk)
    if request.method == 'POST':
        form = ApartmentForm(request.POST)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.property = property
            apartment.save()
            messages.success(request, "Apartment added successfully!")
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
            messages.success(request, "Apartment updated successfully!")
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
        messages.success(request, "Apartment status updated!")
        return redirect('property_detail', pk=apartment.property.pk)
    return render(request, 'listings/update_apartment_status.html', {'apartment': apartment})


@login_required
def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    return render(request, 'listings/apartment_detail.html', {'apartment': apartment})


# ---------- AJAX SEARCH ----------
def search_properties(request):
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')
    max_price = request.GET.get('max_price', '')

    properties = Property.objects.all()

    if location:
        properties = properties.filter(address__icontains=location)
    if property_type:
        properties = properties.filter(property_type__iexact=property_type.capitalize())
    if max_price:
        try:
            max_price = float(max_price)
            properties = [p for p in properties if (p.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0) <= max_price]
        except ValueError:
            pass

    results = [{
        'id': p.id,
        'title': p.title,
        'location': p.address,
        'main_image': p.main_image.url if p.main_image else '',
        'average_rent': p.apartments.aggregate(avg_rent=Avg('rent'))['avg_rent'] or 0,
    } for p in properties]

    return JsonResponse({'results': results})
