from datetime import datetime

import openpyxl
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import models, transaction
from .forms import LoginForm, ImportCSVForm, ImportXLSXForm
from .models import Sponsor, Membre, Equipe, Tournoi, Match, SupportVisibilite, Emplacement, Categorie
from .forms import MembreForm, EquipeForm, TournoiForm, SponsorForm, MatchForm, EmplacementForm, SupportVisibiliteForm, \
    InscriptionForm
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
import csv
import logging


logger = logging.getLogger(__name__)

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

# @login_required
# def liste_sponsors(request):
#     sponsors = Sponsor.objects.all()
#     actif = request.GET.get('actif')
#     if actif == 'oui':
#         sponsors = Sponsor.objects.filter(actif=True)
#     elif actif == 'non':
#         sponsors = Sponsor.objects.filter(actif=False)
#     else:
#         sponsors = Sponsor.objects.all()  # Tous les sponsors par défaut
#     #sponsors = Sponsor.objects.prefetch_related('emplacements').all()
#     #context = {'sponsors': sponsors}
#     #return render(request, 'sponsors/liste_sponsors.html', context)
#     # Prépare les données pour le template
#     sponsors_avec_cout_total = []
#     for sponsor in sponsors:
#         cout_total = sponsor.emplacements.all().aggregate(total=Sum('prix'))['total'] or 0.00
#         sponsors_avec_cout_total.append({
#             'sponsor': sponsor,
#             'cout_total': cout_total,
#         })
#
#     context = {
#         'sponsors_avec_cout_total': sponsors_avec_cout_total,
#     }
#
#     return render(request, 'sponsors/liste_sponsors.html', context)

@login_required
def liste_sponsors(request):
    actif = request.GET.get('actif')
    if actif == 'oui':
        sponsors = Sponsor.objects.filter(actif=True).annotate(
            cout_total=Sum('emplacements__prix')  # <-- Correction ici
        )
    elif actif == 'non':
        sponsors = Sponsor.objects.filter(actif=False).annotate(
            cout_total=Sum('emplacements__prix')  # <-- Correction ici
        )
    else:
        sponsors = Sponsor.objects.all().annotate(
            cout_total=Sum('emplacements__prix')  # <-- Correction ici
        )

    context = {
        'sponsors': sponsors,
    }
    return render(request, 'sponsors/liste_sponsors.html', context)

def calculer_montant_contribution(emplacements):
    result = emplacements.aggregate(total=Sum('prix'))  # Calcule la somme
    return result['total'] or 0  # Gère le cas où il n'y a pas d'emplacements (None)

def detail_sponsor(request, pk):
    sponsor = Sponsor.objects.prefetch_related('emplacements').get(pk=pk)
    #emplacements = Emplacement.objects.filter(sponsor=sponsor,)  # Vous pouvez garder cette ligne si vous avez besoin des emplacements pour autre chose
    montant_contribution = calculer_montant_contribution(sponsor.emplacements.all())
    return render(request, 'sponsors/detail_sponsor.html', {'sponsor': sponsor, 'montant_contribution': montant_contribution, 'emplacements':sponsor.emplacements.all()})

def ajouter_sponsor(request):
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Enregistre le sponsor (sans les emplacements pour l'instant)
            #form.save_m2m() # Enregistre les emplacements après l'enregistrement du sponsor

            return redirect('liste_sponsors')
    else:
        form = SponsorForm()
    return render(request, 'sponsors/ajouter_sponsor.html', {'form': form})


def modifier_sponsor(request, sponsor_id):
    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
    supports = SupportVisibilite.objects.all()

    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            form.save()
            return redirect('liste_sponsors')  # Rediriger vers la liste des sponsors
    else:
        form = SponsorForm(instance=sponsor)

    emplacements_pris = sponsor.emplacements.all()
    montant_contribution = emplacements_pris.aggregate(total=Sum('prix'))['total'] or 0

    # Filtrage des emplacements par support dans la vue
    emplacements_par_support = {}
    for support in supports:
        emplacements_par_support[support] = sponsor.emplacements.filter(support=support)

    return render(request, 'club/modifier_sponsor.html', {
        'sponsor': sponsor,
        'supports': supports,
        'form': form,
        'emplacements_pris': emplacements_pris,
        'montant_contribution': montant_contribution,
        'emplacements_par_support': emplacements_par_support,
    })

def supprimer_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    sponsor.delete()
    return redirect('liste_sponsors')

def supprimer_sponsors(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        if selected_items:
            # Supprimer les sponsors sélectionnés
            Sponsor.objects.filter(id__in=selected_items).delete()
            # Supprimer les membres sélectionnés
            Membre.objects.filter(id__in=selected_items).delete()
            # Ajoutez ici la logique pour les autres modèles si nécessaire
        return redirect('liste_sponsors')  # Redirigez vers la page appropriée
    return redirect('index')  # Redirigez en cas de requête GET

def supprimer_membres(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        if selected_items:
            # Supprimer les membres sélectionnés
            Membre.objects.filter(id__in=selected_items).delete()
            print(f"Redirection vers : {reverse('liste_membres')}")  # Afficher l'URL de redirection
        return redirect('liste_membres')  # Redirigez vers la page appropriée
    print(f"Redirection vers : {reverse('liste_membres')}")  # Afficher l'URL de redirection
    return redirect('index')  # Redirigez en cas de requête GET

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
    return render(request, 'supports/liste_supports.html', context)


def emplacements_par_support(request, support_id):
    emplacements = Emplacement.objects.filter(support_id=support_id)
    data = [{'id': emplacement.id, 'numero': emplacement.numero, 'prix': str(emplacement.prix)} for emplacement in emplacements]
    return JsonResponse(data, safe=False)


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


@login_required
def importer_xlsx_membres(request):
    if request.method == 'POST':
        form = ImportXLSXForm(request.POST, request.FILES)
        if form.is_valid():
            xlsx_file = request.FILES['xlsx_file']
            workbook = openpyxl.load_workbook(xlsx_file)
            sheet = workbook.active
            headers = [cell.value for cell in sheet[1]]
            reader = (dict(zip(headers, (cell.value for cell in row))) for row in sheet.iter_rows(min_row=2))

            with transaction.atomic():
                all_rows = list(reader)  # Lecture de toutes les lignes dans une liste

                email_to_categories = {}  # Dictionnaire pour mapper les emails aux catégories
                for row in all_rows:
                    email = row.get('Email')
                    if email:
                        categories = row.get('Qualité', '').split(',')
                        email_to_categories.setdefault(email, []).extend(categories)

                membres_traites = set()

                for row in all_rows:
                    email = row.get('Email')

                    if email and email not in membres_traites:
                        try:
                            membre, created = Membre.objects.update_or_create(
                                email=email,
                                defaults={
                                    'nom': row.get('Nom', '').capitalize(),
                                    'prenom': row.get('Prenom', '').capitalize(),
                                    'Classe_age': row.get('Classe d\'âge'),
                                    'telephone': row.get('Téléphone'),
                                    'adresse': row.get('Adresse'),
                                    'CP': row.get('CP'),
                                    'Ville': row.get('Ville'),
                                    'date_naissance': row.get('Date Naissance'),
                                }
                            )

                            categories_names = set(email_to_categories.get(email, []))  # Récupérer et nettoyer les catégories
                            categories_instances = []
                            for cat_name in categories_names:
                                cat_name = cat_name.strip()
                                if cat_name:
                                    categorie_instance, _ = Categorie.objects.get_or_create(nom=cat_name)
                                    categories_instances.append(categorie_instance)

                            membre.Categorie.set(categories_instances)

                            membres_traites.add(email)

                            if created:
                                print(f"Nouveau membre créé : {membre}")
                            else:
                                print(f"Membre mis à jour : {membre}")

                        except Exception as e:
                            print(f"Erreur lors de la mise à jour/création du membre '{email}': {e}")
                            raise  # Important pour annuler la transaction en cas d'erreur

            return redirect('liste_membres')

    else:
        form = ImportXLSXForm()
    return render(request, 'membres/importer_membres.html', {'form': form})


@login_required
def exporter_donnees_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donnees.csv"'

    writer = csv.writer(response)

    # Écriture de l'en-tête CSV (noms des colonnes)
    writer.writerow(['Modèle', 'ID', 'Nom', 'Email', 'Téléphone', '...', 'Catégories'])  # Adaptez les noms de colonnes à vos modèles

    # Exportation des données de chaque modèle
    for model, fields in [
        (Membre, ['nom', 'email', 'telephone', 'Categorie']),  # Spécifiez les champs à exporter pour chaque modèle
        (Sponsor, ['nom', 'email', 'telephone', 'montant_contribution']),
        (Equipe, ['nom', 'categorie', 'entraineur', 'membres', 'sponsors']),
        (Tournoi, ['nom', 'date_debut', 'date_fin', 'lieu', 'equipes', 'sponsors']),
        (Match, ['date', 'equipe_domicile', 'equipe_exterieur', 'score_domicile', 'score_exterieur', 'tournois']),
    ]:
        for obj in model.objects.all():
            row = [model.__name__, obj.id]  # Ajout du nom du modèle et de l'ID
            for field in fields:
                value = getattr(obj, field)

                if isinstance(value, models.ManyToManyField):
                    value = ", ".join([str(item) for item in value.all()])  # Gestion des champs ManyToMany
                elif isinstance(value, models.ForeignKey):
                    value = str(value) if value else ""  # Gestion des clés étrangères
                row.append(value)
            writer.writerow(row)

    return response

def importer_donnees_csv(request):
    if request.method == 'POST':
        form = ImportCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            next(reader)  # Sauter la ligne d'en-tête

            with transaction.atomic():
                for row in reader:
                    model_name = row[0]
                    obj_id = row[1]
                    model = None
                    try:
                        model = apps.get_model('club', model_name)
                        if model is None:
                            print(f"Le modèle '{model_name}' n'existe pas dans l'application 'club'.")
                            continue

                        try:
                            obj = model.objects.get(pk=obj_id)
                        except model.DoesNotExist:
                            print(f"L'objet {model_name} avec l'ID {obj_id} n'existe pas dans la base de données")
                            continue

                        fields = [f.name for f in model._meta.get_fields() if f.name not in ['id']]

                        for i, field in enumerate(fields):
                            value = row[i + 2]
                            model_field = model._meta.get_field(field)

                            if isinstance(model_field, models.ManyToManyField):
                                if field == 'emplacements':  # <-- Vérification cruciale du nom du champ
                                    related_model = model_field.related_model
                                    related_ids = value.split(',')

                                    related_objects = []
                                    for related_id in related_ids:
                                        related_id = related_id.strip()

                                        if related_id:
                                            try:
                                                related_obj = related_model.objects.get(pk=int(related_id))
                                                related_objects.append(related_obj)
                                            except related_model.DoesNotExist:
                                                print(f"L'objet {related_model.__name__} avec l'ID {related_id} n'existe pas.")

                                    getattr(obj, field).set(related_objects, clear=True) # clear=True pour remplacer les anciennes valeurs

                                elif field == 'sponsors':  # Gestion du champ 'sponsors' dans Sponsor, Equipe et Tournoi
                                    related_model = model_field.related_model
                                    related_ids = value.split(',')
                                    related_objects = []
                                    for related_id in related_ids:
                                        related_id = related_id.strip()
                                        if related_id:
                                            try:
                                                related_obj = related_model.objects.get(pk=int(related_id))
                                                related_objects.append(related_obj)
                                            except related_model.DoesNotExist:
                                                print(f"L'objet {related_model.__name__} avec l'ID {related_id} n'existe pas.")
                                    getattr(obj, field).set(related_objects, clear=True)

                                elif field == 'membres':  # Gestion du champ 'membres' dans Equipe
                                    related_model = model_field.related_model
                                    related_ids = value.split(',')
                                    related_objects = []
                                    for related_id in related_ids:
                                        related_id = related_id.strip()
                                        if related_id:
                                            try:
                                                related_obj = related_model.objects.get(pk=int(related_id))
                                                related_objects.append(related_obj)
                                            except related_model.DoesNotExist:
                                                print(f"L'objet {related_model.__name__} avec l'ID {related_id} n'existe pas.")
                                    getattr(obj, field).set(related_objects, clear=True)

                                elif field == 'equipes':  # Gestion du champ 'equipes' dans Tournoi
                                    related_model = model_field.related_model
                                    related_ids = value.split(',')
                                    related_objects = []
                                    for related_id in related_ids:
                                        related_id = related_id.strip()
                                        if related_id:
                                            try:
                                                related_obj = related_model.objects.get(pk=int(related_id))
                                                related_objects.append(related_obj)
                                            except related_model.DoesNotExist:
                                                print(f"L'objet {related_model.__name__} avec l'ID {related_id} n'existe pas.")
                                    getattr(obj, field).set(related_objects, clear=True)

                                elif field == 'Categorie':  # Gestion du champ 'Categorie' dans Membre
                                    related_model = model_field.related_model
                                    related_ids = value.split(',')
                                    related_objects = []
                                    for related_id in related_ids:
                                        related_id = related_id.strip()
                                        if related_id:
                                            try:
                                                related_obj = related_model.objects.get(pk=int(related_id))
                                                related_objects.append(related_obj)
                                            except related_model.DoesNotExist:
                                                print(f"L'objet {related_model.__name__} avec l'ID {related_id} n'existe pas.")
                                    getattr(obj, field).set(related_objects, clear=True)

                            elif isinstance(model_field, models.ForeignKey):
                                if value:
                                    try:
                                        related_model = model_field.related_model
                                        related_obj = related_model.objects.get(pk=int(value))
                                        setattr(obj, field, related_obj)
                                    except related_model.DoesNotExist:
                                        print(f"L'objet {related_model.__name__} avec l'ID {value} n'existe pas.")
                                else:
                                    setattr(obj, field, None)

                            elif isinstance(model_field, models.DateField):
                                if value:
                                    try:
                                        setattr(obj, field, datetime.strptime(value, "%Y-%m-%d").date())
                                    except ValueError:
                                        print(f"Erreur de format de date pour le champ {field} : {value}. Format attendu : YYYY-MM-DD")
                                else:
                                    setattr(obj, field, None)

                            else:
                                setattr(obj, field, value)

                        obj.save()
                        print(f"Objet {model_name} avec ID {obj_id} importé.")

                    except LookupError:
                        print(f"Le modèle '{model_name}' n'existe pas ou l'application 'club' est incorrecte.")
                        continue

                    except Exception as e:
                        print(f"Erreur lors de l'importation de l'objet {model_name} avec ID {obj_id} : {e}")
                        # ... (gestion des exceptions)

            return redirect('liste_membres')  # Remplacez 'liste_membres'

    else:
        form = ImportCSVForm()
    return render(request, 'importer_donnees.html', {'form': form})  # Remplacez 'importer_donnees.html'

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
    categories = membre.Categorie.all()  # Récupérer toutes les catégories du membre
    return render(request, 'membres/detail_membre.html', {'membre': membre, 'categories': categories})
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
