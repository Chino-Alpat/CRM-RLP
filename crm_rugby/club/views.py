from django.shortcuts import render, redirect, get_object_or_404
from .models import Membre,Equipe,Tournoi,Sponsor, Match
from .forms import MembreForm, EquipeForm, TournoiForm, SponsorForm, MatchForm

def liste_sponsors(request):
    sponsors = Sponsor.objects.all()
    return render(request, 'liste_sponsors.html', {'sponsors':sponsors})

def ajouter_sponsor(request):
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_sponsors')
    else:
        form = SponsorForm()
    return render(request,'ajouter_sponsor.html', {'form':form})

def modifier_sponsonr(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    if request.method== 'POST':
        form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            form.save()
            return redirect('liste_sponsors')
    else:
        form = SponsorForm(instance=sponsor)
    return render(request, 'modifier_sponsor.html', {'form':form,'sponsor':sponsor})

def supprimer_sponsor(request, pk):
    sponsor = get_object_or_404(Sponsor, pk=pk)
    sponsor.delete()
    return redirect('liste_sponsors')

# Vues pour les Membres

def liste_membres(request):
    membres = Membre.objects.all()
    return render(request, 'liste_membres.html', {'membres': membres})

def ajouter_membre(request):
    if request.method == 'POST':
        form = MembreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_membres')
    else:
        form = MembreForm()
    return render(request, 'ajouter_membre.html', {'form': form})

def modifier_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == 'POST':
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            return redirect('liste_membres')
    else:
        form = MembreForm(instance=membre)
    return render(request, 'modifier_membre.html', {'form': form, 'membre': membre})

def supprimer_membre(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    membre.delete()
    return redirect('liste_membres')

# Vues pour les Equipes

def liste_equipes(request):
    equipes = Equipe.objects.all()
    return render(request, 'liste_equipes.html', {'equipes': equipes})

def ajouter_equipe(request):
    if request.method == 'POST':
        form = EquipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_equipes')
    else:
        form = EquipeForm()
    return render(request, 'ajouter_equipe.html', {'form': form})

def modifier_equipe(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    if request.method == 'POST':
        form = EquipeForm(request.POST, instance=equipe)
        if form.is_valid():
            form.save()
            return redirect('liste_equipes')
    else:
        form = EquipeForm(instance=equipe)
    return render(request, 'modifier_equipe.html', {'form': form, 'equipe': equipe})

def supprimer_equipe(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    equipe.delete()
    return redirect('liste_equipes')

# Vues pour les Tournois

def liste_tournois(request):
    tournois = Tournoi.objects.all()
    return render(request, 'liste_tournois.html', {'tournois': tournois})

def ajouter_tournoi(request):
    if request.method == 'POST':
        form = TournoiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_tournois')
    else:
        form = TournoiForm()
    return render(request, 'ajouter_tournoi.html', {'form': form})

def modifier_tournoi(request, pk):
    tournoi = get_object_or_404(Tournoi, pk=pk)
    if request.method == 'POST':
        form = TournoiForm(request.POST, instance=tournoi)
        if form.is_valid():
            form.save()
            return redirect('liste_tournois')
    else:
        form = TournoiForm(instance=tournoi)
    return render(request, 'modifier_tournoi.html', {'form': form, 'tournoi': tournoi})

def supprimer_tournoi(request, pk):
    tournoi = get_object_or_404(Tournoi, pk=pk)
    tournoi.delete()
    return redirect('liste_tournois')

# Vues pour les Matchs

def liste_matchs(request):
    matchs = Match.objects.all()
    return render(request, 'liste_matchs.html', {'matchs': matchs})

def ajouter_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_matchs')
    else:
        form = MatchForm()
    return render(request, 'ajouter_match.html', {'form': form})

def modifier_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('liste_matchs')
    else:
        form = MatchForm(instance=match)
    return render(request, 'modifier_match.html', {'form': form, 'match': match})

def supprimer_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    match.delete()
    return redirect('liste_matchs')