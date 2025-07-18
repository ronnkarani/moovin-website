
from django.shortcuts import render, redirect, get_object_or_404    
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import UserProfile, Property
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout


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
    properties = Property.objects.all().order_by('-created_at')
    return render(request, 'pages/property.html', {'properties': properties})

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

    # Dummy values for now — update once tenants and repairs are added
    total_properties = properties.count()
    open_repairs = 0  # Placeholder
    total_tenants = 0  # Placeholder

    return render(request, 'pages/landlord.html', {
        'properties': properties,
        'total_properties': total_properties,
        'open_repairs': open_repairs,
        'total_tenants': total_tenants,
    })

def landlord_properties(request):
    return render(request, 'pages/landlord_properties.html')

def landlord_add_property(request):
    if request.method == "POST":
        title = request.POST.get("title")
        location = request.POST.get("location")
        price = request.POST.get("price")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        messages.success(request, "Property submitted successfully!")
        return redirect('landlord_properties')

    return render(request, "pages/landlord_add_property.html")

def landlord_repair_requests(request):
    return render(request, 'pages/landlord_repairs.html')

def tenant_profile(request):
    return render(request, 'pages/tenant_profile.html')

def tenant_request_repair(request):
    if request.method == 'POST':
        pass
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
    return render(request, 'registration/login.html')

def custom_logout_view(request):
    logout(request)
    return redirect('home') 