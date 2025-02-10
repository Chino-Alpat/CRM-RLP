from django.db import models

class SupportVisibilite(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    nombre_emplacements = models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.nom

    @property
    def prix(self):
        return sum(emplacement.prix for emplacement in self.emplacements.all())

class Sponsor(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos_sponsors/', blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    type_partenariat = models.CharField(max_length=100, blank=True, null=True)
    montant_contribution = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nom


class Emplacement(models.Model):
    support = models.ForeignKey(SupportVisibilite, on_delete=models.CASCADE, related_name='emplacements')
    numero = models.PositiveIntegerField()
    sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, blank=True, null=True, related_name='emplacements')
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Prix de l'emplacement
    duree_engagement = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True, help_text="Durée de l'engagement en mois")
    date_debut = models.DateField(blank=True, null=True, help_text="Date de début de l'engagement")
    date_fin = models.DateField(blank=True, null=True, help_text="Date de fin de l'engagement")

    class Meta:
        unique_together = ('support', 'numero')

    def __str__(self):
        return f"Emplacement {self.numero} sur {self.support}"


class Membre(models.Model):
    username = models.CharField(max_length=100,blank=True, null=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    surnom = models.CharField(max_length=100, blank=True, null=True)
    license = models.CharField(max_length=13, blank=True, null=True)
    photo = models.ImageField(upload_to='photo_id/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"
class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=100)
    entraineur = models.ForeignKey(Membre, on_delete=models.SET_NULL, blank=True, null=True, related_name='equipes_entrainees')
    membres = models.ManyToManyField(Membre, related_name='equipes_jouees')
    sponsors = models.ManyToManyField(Sponsor, related_name='equipes_sponsorisees', blank=True)

    def __str__(self):
        return self.nom
class Tournoi(models.Model):
    nom = models.CharField(max_length=100)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    lieu = models.CharField(max_length=100, blank=True, null=True)
    equipes = models.ManyToManyField(Equipe, related_name='Tournois_participes')
    sponsors = models.ManyToManyField(Sponsor, related_name='tournois_sponsorises', blank=True)

    def __str__(self):
        return self.nom

class Match(models.Model):
    date = models.DateField(blank=True, null=True)
    equipe_domicile = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='match_domicile')
    equipe_exterieur = models.ForeignKey(Equipe, on_delete=models.CASCADE,related_name='match_exterieur')
    score_domicile = models.PositiveIntegerField(blank=True, null=True)
    score_exterieur = models.PositiveIntegerField(blank=True, null=True)
    tournois = models.ForeignKey(Tournoi, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nom
