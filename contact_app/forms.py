from django import forms
from .models import Professional

class ProfessionalForm(forms.ModelForm):
    class Meta:
        model = Professional
        fields = ['first_name', 'last_name', 'email', 'phone', 'state', 'expertise', 'service_cost_per_hour']
        widgets = {
            'expertise': forms.Select(choices=Professional.EXPERTISE_CHOICES)
        }