from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # URL pour les Sponsors
    path('sponsors/', views.liste_sponsors, name='liste_sponsors'),
    path('sponsors/ajouter/', views.ajouter_sponsor, name='ajouter_sponsor'),
    path('sponsors/<int:pk>/modifier/', views.modifier_sponsor, name='modifier_sponsor'),
    path('sponsors/<int:pk>/supprimer/', views.supprimer_sponsor, name='supprimer_sponsor'),
    path('sponsors/<int:pk>/', views.detail_sponsor, name='detail_sponsor'),

    # URL pour les Membres
    path('membres/', views.liste_membres, name='liste_membres'),
    path('membres/ajouter/', views.ajouter_membre, name='ajouter_membre'),
    path('membres/<int:pk>/modifier/', views.modifier_membre, name='modifier_membre'),
    path('membres/<int:pk>/supprimer/', views.supprimer_membre, name='supprimer_membre'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('membres/inscription/', views.inscription, name='inscription'),
    path('membre/<int:pk>/', views.detail_membre, name='detail_membre'),

    # URL pour les Équipes
    path('equipes/', views.liste_equipes, name='liste_equipes'),
    path('equipes/ajouter/', views.ajouter_equipe, name='ajouter_equipe'),
    path('equipes/<int:pk>/modifier/', views.modifier_equipe, name='modifier_equipe'),
    path('equipes/<int:pk>/supprimer/', views.supprimer_equipe, name='supprimer_equipe'),
    path('equipe/<int:pk>/', views.detail_equipe, name='detail_equipe'),

    # URL pour les Tournois
    path('tournois/', views.liste_tournois, name='liste_tournois'),
    path('tournois/ajouter/', views.ajouter_tournoi, name='ajouter_tournoi'),
    path('tournois/<int:pk>/modifier/', views.modifier_tournoi, name='modifier_tournoi'),
    path('tournois/<int:pk>/supprimer/', views.supprimer_tournoi, name='supprimer_tournoi'),

    # URL pour les Matchs
    path('matchs/', views.liste_matchs, name='liste_matchs'),
    path('matchs/ajouter/', views.ajouter_match, name='ajouter_match'),
    path('matchs/<int:pk>/modifier/', views.modifier_match, name='modifier_match'),
    path('matchs/<int:pk>/supprimer/', views.supprimer_match, name='supprimer_match'),

    # URL pour les Supports de Visibilité
    path('supports/', views.liste_supports, name='liste_supports'),
    path('supports/ajouter/', views.ajouter_support, name='ajouter_support'),
    path('supports/<int:pk>/modifier/', views.modifier_support, name='modifier_support'),
    path('supports/<int:pk>/supprimer/', views.supprimer_support, name='supprimer_support'),

    # URL pour les Emplacements
    path('emplacements/', views.liste_emplacements, name='liste_emplacements'),
    path('emplacements/ajouter/', views.ajouter_emplacement, name='ajouter_emplacement'),
    path('emplacements/<int:pk>/modifier/', views.modifier_emplacement, name='modifier_emplacement'),
    path('emplacements/<int:pk>/supprimer/', views.supprimer_emplacement, name='supprimer_emplacement'),
]