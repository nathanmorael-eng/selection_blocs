from django import forms

from .models import Boulder, User


class ImportExcelForm(forms.Form):
    fichier = forms.FileField(label="Fichier Excel (.xlsx)")

    def clean_fichier(self):
        fichier = self.cleaned_data["fichier"]
        if not fichier.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Le fichier doit être au format .xlsx")
        return fichier


class AjouterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "telephone", "date_naissance",
            "sexe", "niveau", "annee",
            "dispo_lundi", "dispo_mardi", "dispo_creneaux_compet", "dispo_creneaux_perf",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "dispo_lundi": "Dispo lundi",
            "dispo_mardi": "Dispo mardi",
            "dispo_creneaux_compet": "Dispo créneaux compét",
            "dispo_creneaux_perf": "Dispo créneaux perf",
        }


class BoulderForm(forms.ModelForm):
    class Meta:
        model = Boulder
        fields = ["numero", "name", "location"]
