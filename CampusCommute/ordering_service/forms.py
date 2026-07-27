from django import forms
from .models import RideOrder


class RideOrderForm(forms.ModelForm):
    class Meta:
        model  = RideOrder
        fields = [
            'pickup_location', 'dropoff_location',
            'pickup_lat', 'pickup_lng',
            'approx_time', 'num_passengers', 'description',
        ]
        widgets = {
            'pickup_lat':  forms.HiddenInput(),
            'pickup_lng':  forms.HiddenInput(),
            'approx_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'pickup_location':  forms.TextInput(attrs={'placeholder': 'e.g. North Campus Gate'}),
            'dropoff_location': forms.TextInput(attrs={'placeholder': 'e.g. Student Union'}),
            'description':      forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any notes for the driver...'}),
        }
