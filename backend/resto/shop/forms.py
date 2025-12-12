from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class SignupForm(UserCreationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        min_length=6,
        max_length=30,
        help_text="Entre 6 et 30 caractères.",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nom d'utilisateur",
        }),
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Mot de passe",
        }),
    )

    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirmer le mot de passe",
        }),
    )

    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        # sécurité : recheck longueur côté serveur
        if len(username) < 6:
            raise forms.ValidationError("Le nom d'utilisateur doit contenir au moins 6 caractères.")
        if len(username) > 30:
            raise forms.ValidationError("Le nom d'utilisateur ne doit pas dépasser 30 caractères.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label="Nom", max_length=150)
    phone = forms.CharField(label="Téléphone", max_length=30)
    address = forms.CharField(label="Adresse / Lieu de livraison", widget=forms.Textarea)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'address']

 



 
from .models import Meal

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ["category", "name", "slug", "description", "price", "is_active", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
