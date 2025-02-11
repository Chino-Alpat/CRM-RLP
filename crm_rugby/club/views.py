from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, ImportCSVForm
from .models import Sponsor, Membre, Equipe, Tournoi, Match, SupportVisibilite, Emplacement
from .forms import MembreForm, EquipeForm, TournoiForm, SponsorForm, MatchForm, EmplacementForm, SupportVisibiliteForm, \
    InscriptionForm
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
import csv

def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Rediriger vers la page d'accueil après la connexion
            else:
                form.add_error(None, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'index.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Rediriger vers la page d'accueil après la connexion
            else:
                form.add_error(None, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')  # Rediriger vers la page d'accueil après la déconnexion

# Vues pour les Emplacements

def liste_emplacements(request):
    emplacements = Emplacement.objects.all()
    return render(request, 'emplacements/liste_emplacements.html', {'emplacements': emplacements})

@login_required
def ajouter_emplacement(request):
    if request.method == 'POST':
        form = EmplacementForm(request.POST)
        if form.is_valid():
            emplacement = form.save(commit=False)
            if emplacement.date_debut and emplacement.duree_engagement:
                emplacement.date_fin = emplacement.date_debut + relativedelta(months=emplacement.duree_engagement)
            emplacement.save()
            return redirect('liste_emplacements')
    else:
        form = EmplacementForm()
    return render(request, 'emplacements/ajouter_emplacement.html', {'form': form})

@login_required
def modifier_emplacement(request, pk):
    emplacement = get_object_or_404(Emplacement, pk=pk)
    if request.method == 'POST':
        form = EmplacementForm(request.POST, instance=emplacement)
        if form.is_valid():
            emplacement = form.save(commit=False)
            if emplacement.date_debut and emplacement.duree_engagement:
                emplacement.date_fin = emplacement.date_debut + relativedelta(months=emplacement.duree_engagement)
            emplacement.save()
            return redirect('liste_emplacements')
    else:
        form = EmplacementForm(instance=emplacement)
    return render(request, 'emplacements/modifier_emplacement.html', {'form': form, 'emplacement': emplacement})

@login_required
def supprimer_emplacement(request, pk):
    emplacement = get_object_or_404(Emplacement, pk=pk)
    emplacement.delete()
    return redirect('liste_emplacements')

@login_required
def liste_sponsors(request):
    sponsors = Sponsor.objects.all()

    # Prépare les données pour le template
    sponsors_avec_cout_total = []
    for sponsor in sponsors:
        cout_total = sponsor.emplacements.all().aggregate(total=Sum('prix'))['total'] or 0.00
        sponsors_avec_cout_total.append({
            'sponsor': sponsor,
            'cout_total': cout_total,
        })

    context = {
        'sponsors_avec_cout_total': sponsors_avec_cout_total,
    }

    return render(request, 'sponsors/liste_sponsors.html', context)

def calculer_montant_contribution(emplacements):
    montant = 0
    for emplacement in emplacements:
        montant += emplacement.prix # Exemple : additionner le prix de chaque emplacement
    return montant

def detail_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    emplacements = Emplacement.objects.filter(sponsor=sponsor)
    montant_contribution = calculer_montant_contribution(emplacements)
    return render(request, 'sponsors/detail_sponsor.html', {'sponsor': sponsor,'montant_contribution':montant_contribution })


def ajouter_sponsor(request):
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            sponsor = form.save()
            emplacements = request.POST.getlist('emplacements')
            for emplacement_id in emplacements:
                emplacement = Emplacement.objects.get(pk=emplacement_id)
                emplacement.sponsor = sponsor
                emplacement.save()
            return redirect('liste_sponsors')
    else:
        form = SponsorForm()
        # Emplacements disponibles (non occupés)
        emplacements_disponibles = Emplacement.objects.filter(sponsor=None)
        supports = SupportVisibilite.objects.all()
        # emplacements = Emplacement.objects.filter(sponsor=None) # Emplacements non occupés
    return render(request, 'sponsors/ajouter_sponsor.html', {
        'form': form,
        'emplacements': emplacements_disponibles,
        'supports': supports,
    })


def modifier_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            sponsor = form.save()
            # Réinitialiser les emplacements occupés par ce sponsor
            Emplacement.objects.filter(sponsor=sponsor).update(sponsor=None)
            emplacements = request.POST.getlist('emplacements')
            for emplacement_id in emplacements:
                emplacement = Emplacement.objects.get(pk=emplacement_id)
                emplacement.sponsor = sponsor
                emplacement.save()

            return redirect('liste_sponsors')
    else:
        form = SponsorForm(instance=sponsor)
        # Emplacements disponibles et emplacements pris par ce sponsor
        supports = SupportVisibilite.objects.all()
        emplacements = Emplacement.objects.filter(Q(sponsor=None) | Q(sponsor=sponsor))
        emplacements_spo = Emplacement.objects.filter(sponsor=sponsor)
        montant_contribution = calculer_montant_contribution(emplacements_spo)
        emplacements_disponibles = Emplacement.objects.filter(sponsor=None)

    return render(request, 'sponsors/modifier_sponsor.html', {
        'form': form,
        'sponsor': sponsor,
        'emplacements': emplacements,
        'emplacements_disponibles': emplacements_disponibles,
        'supports': supports,
        'montant_contribution': montant_contribution,
    })


def supprimer_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    sponsor.delete()
    return redirect('liste_sponsors')


# Vues pour les Supports de Visibilité
@login_required
def liste_supports(request):
    supports_visibilite = SupportVisibilite.objects.all()

    # Calculer le coût total pour chaque support
    supports_avec_cout_total = []
    for support in supports_visibilite:
        cout_total = support.emplacements.all().aggregate(total=Sum('prix'))['total'] or 0.00  # Gérer le cas None
        supports_avec_cout_total.append({
            'support': support,
            'cout_total': cout_total,
        })

    context = {
        'supports_avec_cout_total': supports_avec_cout_total,
    }
    print(context)
    return render(request, 'supports/liste_supports.html', context)

def importer_csv_sponsors(request):
    if request.method == 'POST':
        form = ImportCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines(), delimiter=';')
            for row in reader:
                print(row)
                # Créer ou mettre à jour un partenaire en fonction des données du CSV
                partenaire, created = Sponsor.objects.update_or_create(
                    nom=row['SURNOM'],
                    defaults={
                        'email': row['EMAIL'],
                        'telephone': row['SMS'],
                        'contact': f"{row['FIRSTNAME'].capitalize()} {row['LASTNAME'].capitalize()}"
                        # ... autres champs
                    }
                )
            return redirect('liste_sponsors') # Rediriger vers la page de liste des partenaires
    else:
        form = ImportCSVForm()
    return render(request, 'sponsors/importer_sponsors.html', {'form': form})

def ajouter_support(request):
    if request.method == 'POST':
        form = SupportVisibiliteForm(request.POST)
        if form.is_valid():
            support = form.save()
            for i in range(support.nombre_emplacements):
                numero = i + 1
                prix = request.POST.get(f'prix_emplacement_{numero}', 0.00)  # Récupérer le prix depuis le formulaire
                Emplacement.objects.create(support=support, numero=numero, prix=prix)
            return redirect('liste_supports')
    else:
        form = SupportVisibiliteForm()
    return render(request, 'supports/ajouter_support.html', {'form': form})


def modifier_support(request, pk):
    support = get_object_or_404(SupportVisibilite, pk=pk)
    if request.method == 'POST':
        form = SupportVisibiliteForm(request.POST, instance=support)
        if form.is_valid():
            support.save()
            for emplacement in support.emplacements.all():
                prix = request.POST.get(f'prix_emplacement_{emplacement.numero}', 0.00)
                emplacement.prix = prix
                emplacement.save()
            return redirect('liste_supports')
    else:
        form = SupportVisibiliteForm(instance=support)
    return render(request, 'supports/modifier_support.html', {'form': form, 'support': support})


def supprimer_support(request, pk):
    support = get_object_or_404(SupportVisibilite, pk=pk)
    support.delete()
    return redirect('liste_supports')


# Vues pour les Membres
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)  # Incluez request.FILES pour gérer l'upload de photos
        if form.is_valid():
            user = form.save()  # Enregistrez l'utilisateur
            return redirect('page_de_redirection')  # Redirigez l'utilisateur vers une page de confirmation ou de connexion
    else:
        form = InscriptionForm()
    return render(request, 'inscription.html', {'form': form})
@login_required
def liste_membres(request):
    membres = Membre.objects.all()
    return render(request, 'membres/liste_membres.html', {'membres': membres})


def ajouter_membre(request):
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_membres')
    else:
        form = MembreForm()
    return render(request, 'membres/ajouter_membre.html', {'form': form})


def modifier_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES, instance=membre)
        if form.is_valid():
            form.save()
            return redirect('liste_membres')
    else:
        form = MembreForm(instance=membre)
    return render(request, 'membres/modifier_membre.html', {'form': form, 'membre': membre})


def supprimer_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    membre.delete()
    return redirect('liste_membres')

def detail_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    return render(request, 'membres/detail_membre.html', {'membre': membre})
# Vues pour les Equipes

def liste_equipes(request):
    equipes = Equipe.objects.all()
    return render(request, 'equipes/liste_equipes.html', {'equipes': equipes})


def ajouter_equipe(request):
    if request.method == 'POST':
        form = EquipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_equipes')
    else:
        form = EquipeForm()
    return render(request, 'equipes/ajouter_equipe.html', {'form': form})


def modifier_equipe(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    if request.method == 'POST':
        form = EquipeForm(request.POST, instance=equipe)
        if form.is_valid():
            form.save()
            return redirect('liste_equipes')
    else:
        form = EquipeForm(instance=equipe)
    return render(request, 'equipes/modifier_equipe.html', {'form': form, 'equipe': equipe})


def supprimer_equipe(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    equipe.delete()
    return redirect('liste_equipes')

def detail_equipe(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    return render(request, 'equipes/detail_equipe.html', {'equipe': equipe})
# Vues pour les Tournois

def liste_tournois(request):
    tournois = Tournoi.objects.all()
    return render(request, 'tournois/liste_tournois.html', {'tournois': tournois})


def ajouter_tournoi(request):
    if request.method == 'POST':
        form = TournoiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_tournois')
    else:
        form = TournoiForm()
    return render(request, 'tournois/ajouter_tournoi.html', {'form': form})


def modifier_tournoi(request, pk):
    tournoi = get_object_or_404(Tournoi, pk=pk)
    if request.method == 'POST':
        form = TournoiForm(request.POST, instance=tournoi)
        if form.is_valid():
            form.save()
            return redirect('liste_tournois')
    else:
        form = TournoiForm(instance=tournoi)
    return render(request, 'tournois/modifier_tournoi.html', {'form': form, 'tournoi': tournoi})


def supprimer_tournoi(request, pk):
    tournoi = get_object_or_404(Tournoi, pk=pk)
    tournoi.delete()
    return redirect('liste_tournois')


# Vues pour les Matchs

def liste_matchs(request):
    matchs = Match.objects.all()
    return render(request, 'match/liste_matchs.html', {'matchs': matchs})


def ajouter_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_matchs')
    else:
        form = MatchForm()
    return render(request, 'match/ajouter_match.html', {'form': form})


def modifier_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('liste_matchs')
    else:
        form = MatchForm(instance=match)
    return render(request, 'match/modifier_match.html', {'form': form, 'match': match})


def supprimer_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    match.delete()
    return redirect('liste_matchs')
