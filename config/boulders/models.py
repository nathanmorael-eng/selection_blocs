from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Boulder(models.Model):
    name = models.CharField(max_length=200)
    grade = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    

    def __str__(self):
        return self.name

class User(AbstractUser):
    SEXE_CHOICES = [
        ("H", "Homme"),
        ("F", "Femme"),
    ]

    # Nom -> last_name, Prenom -> first_name : deja herites d'AbstractUser, pas besoin de les redefinir

    email = models.EmailField(unique=True)  # unique pour eviter les doublons lors de l'import Excel
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, blank=True)
    niveau = models.CharField(max_length=20, blank=True)  # cotation arkose

    dispo_lundi = models.BooleanField(default=False)
    dispo_mardi = models.BooleanField(default=False)
    dispo_creneaux_compet = models.BooleanField(default=False)
    dispo_creneaux_perf = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Ascent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ascents')
    boulder = models.ForeignKey(Boulder, on_delete=models.CASCADE, related_name='ascents')

    class Meta:
        unique_together = ('user', 'boulder')

    def __str__(self):
        return f'{self.user} - {self.boulder}'


