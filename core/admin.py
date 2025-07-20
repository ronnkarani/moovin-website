# core/admin.py
from django.contrib import admin
from .models import UserProfile, Property, PropertyImage, RepairRequest


admin.site.register(RepairRequest)  # register it
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3  # Allow 3 extra image upload slots

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]
    list_display = ('title', 'location', 'price', 'property_type', 'status', 'furnished', 'landlord')
    search_fields = ('title', 'location', 'status')
    list_filter = ('status', 'furnished', 'bedrooms', 'bathrooms')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    
