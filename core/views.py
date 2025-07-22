from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RepairRequestForm
from django.shortcuts import render, redirect, get_object_or_404    
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import UserProfile, Property, RepairRequest
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from .forms import PropertyForm, RepairRequestForm, RepairStatusForm
from .models import RepairRequest, Property  # Make sure Repair is imported
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class CustomLoginView(LoginView):
    template_name = 'pages/login.html'

    def get_success_url(self):
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            role = user_profile.role

            if role == 'admin':
                return reverse('admin:index')
            elif role == 'landlord':
                return reverse('landlord')
            elif role == 'tenant':
                return reverse('tenant_profile')
        except UserProfile.DoesNotExist:
            messages.error(self.request, "User profile not found.")
            return reverse('home')
        return reverse('home')

def home(request):
    return render(request, 'pages/home.html', {})

def contact(request):
    return render(request, 'pages/contact.html')


def property_list(request):
    properties = Property.objects.all()

    # Get filter values from query params
    location = request.GET.get('location')
    property_type = request.GET.get('type')
    price_range = request.GET.get('price')

     # Filter location
    if location and location != "All Locations":
        properties = properties.filter(location__icontains=location)

    # Filter type
    if property_type and property_type != "All Types":
        properties = properties.filter(property_type__iexact=property_type)

    # Filter price
    if price_range:
        if price_range == "Below Ksh 10K":
            properties = properties.filter(price__lt=10000)
        elif price_range == "10K - 30K":
            properties = properties.filter(price__gte=10000, price__lte=30000)

     # --- Pagination ---
    paginator = Paginator(properties, 4)
    page = request.GET.get('page')

    try:
        page_number = int(page)
        if page_number < 1:
            page_number = 1
    except (TypeError, ValueError):
        page_number = 1

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        # If page is too high, show last page
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'properties': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'pages/property.html', context)

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'pages/property_details.html', {'property': property})

@login_required
def landlord_dashboard(request):
    user = request.user

    # Check user is a landlord
    try:
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.role != 'landlord':
            return redirect('home')  # or show an error
    except UserProfile.DoesNotExist:
        return redirect('home')

    # Get properties for this landlord
    properties = Property.objects.filter(landlord=user)
    
    # Fetch repair requests for this landlord
    repair_requests = RepairRequest.objects.filter(property__landlord=user)
    
    # Dummy values for now — update once tenants and repairs are added
    total_properties = properties.count()
    open_repairs = repair_requests.count()  # 👈 Count all related repairs
    total_tenants = 0  # Placeholder
    
    # Fetch repair requests for this landlord
    repair_requests = RepairRequest.objects.filter(property__landlord=user)
    

    return render(request, 'pages/landlord.html', {
        'properties': properties,
        'repair_requests': repair_requests,
        'total_properties': total_properties,
        'open_repairs': open_repairs,
        'total_tenants': total_tenants,
    })


@login_required
def landlord_properties(request):
    landlord = request.user
    properties = Property.objects.filter(landlord=landlord)
    return render(request, 'pages/landlord_properties.html', {'properties': properties})

@login_required
def landlord_add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user  # Assign landlord here
            property.save()
            return redirect('landlord_properties')
    else:
        form = PropertyForm()
    return render(request, 'pages/landlord_add_property.html', {'form': form})


@login_required
def landlord_repair_requests(request):
    landlord = request.user
    properties = Property.objects.filter(landlord=landlord)
    
     # Fetch repair requests for properties owned by the landlord
    repair_requests = RepairRequest.objects.filter(property__landlord=landlord)

    # Count of all repair requests
    open_repairs = repair_requests.count()
    
    context = {
        'repair_requests': repair_requests,
        'open_repairs': open_repairs,
    }
    return render(request, 'pages/landlord_repairs.html', context)

class TenantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/tenant_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get the property this tenant is renting
        property_rented = Property.objects.filter(tenant=user).first()

        # Get all repair requests made by this tenant
        repair_requests = RepairRequest.objects.filter(tenant=user).order_by('-created_at')

        context.update({
            'tenant': user,
            'property_rented': property_rented,
            'repair_requests': repair_requests,
        })
        return context

@login_required
def tenant_request_repair(request):
    if request.method == 'POST':
        issue = request.POST.get('description')
        tenant = request.user

        # Get the tenant's property
        property_rented = Property.objects.filter(tenant=tenant).first()

        if property_rented and issue:
            RepairRequest.objects.create(
                tenant=tenant,
                property=property_rented,
                issue=issue
            )
            messages.success(request, "Repair request submitted successfully.")
            return redirect('tenant_profile')
        else:
            messages.error(request, "You must be assigned a property to submit a repair request.")

    return render(request, 'pages/tenant_request_repair.html')


@never_cache
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.userprofile.role == 'Landlord':
                return redirect('landlord')
            elif user.userprofile.role == 'Tenant':
                return redirect('tenant_profile')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'pages/login.html')

def custom_logout_view(request):
    logout(request)
    return redirect('home') 


@login_required
def update_repair_status(request, repair_id):
    repair = get_object_or_404(RepairRequest, id=repair_id)

    if request.method == 'POST':
        form = RepairStatusForm(request.POST, instance=repair)
        if form.is_valid():
            form.save()
            return redirect('landlord_repair_requests')  # redirect after update
    else:
        form = RepairStatusForm(instance=repair)

    return render(request, 'pages/update_requests_form.html', {'form': form, 'repair': repair})


@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk, landlord=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully.")
            return redirect('landlord')  # or 'landlord_properties'
    else:
        form = PropertyForm(instance=property)

    return render(request, 'pages/edit_property.html', {'form': form, 'property': property})
