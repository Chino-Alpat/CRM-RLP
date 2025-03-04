from django import forms
from django.db.models import Q
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance: # Si on est dans le cadre d'une modification
            self.fields['emplacements'].queryset = Emplacement.objects.filter(
                Q(sponsor_emplacements__isnull=True) | Q(sponsor_emplacements=self.instance)
            )
        else: # Si c'est une création
            self.fields['emplacements'].queryset = Emplacement.objects.filter(sponsor_emplacements__isnull=True)  # Emplacements libres uniquement

    emplacements = forms.ModelMultipleChoiceField(
        #queryset=Emplacement.objects.filter(sponsor_emplacements__isnull=True),  # Tous les emplacements disponibles
        queryset=Emplacement.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Widget pour la sélection multiple
        #widget=forms.HiddenInput(),  # Utiliser un widget caché
        #widget=forms.MultiWidget(widgets=[forms.CheckboxSelectMultiple, forms.HiddenInput()]),  # Utiliser un widget caché
        required=False  # Permettre de ne pas sélectionner d'emplacements
    )

    class Meta:
        model = Sponsor
        fields = '__all__'  # Ou spécifiez les champs que vous voulez inclure
        widgets = {
            'montant_contribution': forms.HiddenInput(),
        }

class ImportCSVForm(forms.Form):
    csv_file = forms.FileField(label='Fichier CSV')

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
class ImportCSVForm(forms.Form):
    csv_file = forms.FileField(label='Fichier CSV')
class ImportXLSXForm(forms.Form):
    xlsx_file = forms.FileField(label='Fichier XLSX')

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