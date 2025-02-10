# Generated by Django 5.1.5 on 2025-02-06 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_emplacement_date_debut_emplacement_date_fin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='membre',
            name='username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='emplacement',
            name='duree_engagement',
            field=models.DecimalField(blank=True, decimal_places=0, help_text="Durée de l'engagement en mois", max_digits=2, null=True),
        ),
    ]
