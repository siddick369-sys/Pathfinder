from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label='Prénom', widget=forms.TextInput(attrs={
        'placeholder': 'Ex: Amadou', 'class': 'form-input'
    }))
    last_name = forms.CharField(max_length=50, label='Nom', widget=forms.TextInput(attrs={
        'placeholder': 'Ex: Diallo', 'class': 'form-input'
    }))
    email = forms.EmailField(label='Adresse email', widget=forms.EmailInput(attrs={
        'placeholder': 'etudiant@universite.cm', 'class': 'form-input'
    }))
    filiere = forms.ChoiceField(choices=CustomUser.FILIERE_CHOICES, label='Filière', widget=forms.Select(attrs={
        'class': 'form-input'
    }))
    niveau = forms.ChoiceField(choices=CustomUser.NIVEAU_CHOICES, label='Niveau', widget=forms.Select(attrs={
        'class': 'form-input'
    }))

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'filiere', 'niveau', 'username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': '••••••••'})


class LoginForm(forms.Form):
    username = forms.CharField(label='Nom d\'utilisateur', widget=forms.TextInput(attrs={
        'placeholder': 'Votre identifiant', 'class': 'form-input'
    }))
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={
        'placeholder': '••••••••', 'class': 'form-input'
    }))
