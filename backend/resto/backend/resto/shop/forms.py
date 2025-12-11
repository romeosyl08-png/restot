from django import forms
from .models import UserProfile


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label="Nom", max_length=150)
    phone = forms.CharField(label="Téléphone", max_length=30)
    address = forms.CharField(label="Adresse / Lieu de livraison", widget=forms.Textarea)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'address']
