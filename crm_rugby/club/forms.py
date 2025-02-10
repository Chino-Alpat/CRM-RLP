from django import forms
from django_flatpickr.schemas import FlatpickrOptions
from django_flatpickr.widgets import DatePickerInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Membre, Equipe, Tournoi, Sponsor, Match, SupportVisibilite, Emplacement

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Nom d\'utilisateur', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class InscriptionForm(UserCreationForm):
    class Meta:
        model = Membre  # Utilisez votre modèle Membre
        fields = ('username', 'email', 'nom', 'prenom', 'license')

class SupportVisibiliteForm(forms.ModelForm):
    class Meta:
        model = SupportVisibilite
        fields = ['nom', 'description', 'nombre_emplacements']

class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = '__all__'
        widgets = {
                    'montant_contribution': forms.HiddenInput(), # Rendre le champ caché
                }
class EmplacementForm(forms.ModelForm):
    class Meta:
        model = Emplacement
        fields = '__all__'
        widgets = {
            'date_debut': DatePickerInput(options=FlatpickrOptions(
                altFormat="d/m/Y",  # Display format (e.g., 25/12/2024)
            )),
            'date_fin': DatePickerInput(options=FlatpickrOptions(
                altFormat="d/m/Y",  # Display format (e.g., 25/12/2024)
            )),
        }
class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = '__all__'
        widgets = {
            'date_naissance': DatePickerInput(options=FlatpickrOptions(
                altFormat="d/m/Y",  # Display format (e.g., 25/12/2024)
            )),  # Format de date
        }
class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = '__all__'


class TournoiForm(forms.ModelForm):
    class Meta:
        model = Tournoi
        fields = '__all__'
        widgets = {
            'date_debut': DatePickerInput(options=FlatpickrOptions(
                altFormat="d/m/Y",  # Display format (e.g., 25/12/2024)
            )),  # Format de date
            'date_fin': DatePickerInput(options=FlatpickrOptions(
                altFormat="d/m/Y",  # Display format (e.g., 25/12/2024)
            )),  # Format de date
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'