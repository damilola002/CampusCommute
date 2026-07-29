from django import forms 
from .models import Rider_user
class riders(forms.ModelForm):
    class Meta: 
        order = Rider_user
        fields = ['description']

    def clean_description(self):
        description = self.cleaned_data.get("description")
        #add some cuton validation here 
        return description