from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from core.views import property_list
from django.contrib.auth.views import LogoutView
from .views import custom_logout_view
from .views import TenantDashboardView


urlpatterns = [
    path('', views.home, name='home'), 
    
    path('contact/', views.contact, name='contact'),
    
    path('property/', views.property_list, name='property'),
    
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    
    path('landlord/properties/<int:pk>/edit/', views.edit_property, name='edit_property'),

    
    path('landlord/', views.landlord_dashboard, name='landlord'),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    
    path('logout/', custom_logout_view, name='logout'),   
        
    path('landlord/properties/', views.landlord_properties, name='landlord_properties'),
    
    path('landlord/properties/add/', views.landlord_add_property, name='landlord_add_property'),
    
    path('landlord/repairs/', views.landlord_repair_requests, name='landlord_repair_requests'),
    
path('repairs/<int:repair_id>/mark-fixed/', views.update_repair_status, name='update_repair_status'),

    
    path('tenant/profile/', TenantDashboardView.as_view(), name='tenant_profile'),
    
    path('tenant/request-repair/', views.tenant_request_repair, name='tenant_request_repair'),

]


