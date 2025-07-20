# core/forms.py

from django import forms
from .models import RepairRequest, Property

class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['property', 'issue']
        widgets = {
            'issue': forms.Textarea(attrs={'rows': 4}),
        }


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'location', 'price', 'image', 'description']


class RepairStatusForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['status']  # landlords can update these only