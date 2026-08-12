from django import forms


class ImportExcelForm(forms.Form):
    fichier = forms.FileField(label="Fichier Excel (.xlsx)")

    def clean_fichier(self):
        fichier = self.cleaned_data["fichier"]
        if not fichier.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Le fichier doit être au format .xlsx")
        return fichier
