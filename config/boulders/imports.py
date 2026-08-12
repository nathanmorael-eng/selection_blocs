import datetime as dt
import zipfile

import openpyxl
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from openpyxl.utils.exceptions import InvalidFileException

from .models import User
from .utils import generer_username, mot_de_passe_initial, normaliser_telephone

# ordre attendu des colonnes dans le fichier Excel (a partir de la ligne 2)
NB_COLONNES = 12


class FichierIllisible(Exception):
    pass


def _resoudre_choice(valeur, choices):
    """Fait correspondre une cellule Excel (code OU libelle humain, ex: 'Bleu' ou 'B')
    a un code de `choices`. Renvoie None si aucune correspondance."""
    if valeur is None or str(valeur).strip() == "":
        return ""
    texte = str(valeur).strip()
    codes = {code for code, _ in choices}
    if texte in codes:
        return texte
    labels = {label.strip().lower(): code for code, label in choices}
    return labels.get(texte.lower())


def _parser_date(valeur):
    if isinstance(valeur, dt.datetime):
        return valeur.date()
    if isinstance(valeur, dt.date):
        return valeur
    return dt.datetime.strptime(str(valeur).strip(), "%d/%m/%Y").date()


def importer_excel(fichier):
    """Lit un classeur Excel (colonnes: Nom, Prenom, Mail, Telephone, Cursus, Sexe,
    Date de naissance, Niveau, Dispo lundi, Dispo mardi, Dispo compet, Dispo perf)
    et cree un User par ligne valide.

    Renvoie (nb_crees, erreurs) ou erreurs est une liste de (numero_ligne, message).
    """
    try:
        classeur = openpyxl.load_workbook(fichier, data_only=True)
    except (InvalidFileException, zipfile.BadZipFile, KeyError):
        raise FichierIllisible("le fichier n'a pas pu être lu (n'est-ce pas un vrai .xlsx ?)")

    feuille = classeur.worksheets[0]

    nb_crees = 0
    erreurs = []

    for i, ligne in enumerate(
        feuille.iter_rows(min_row=2, max_col=NB_COLONNES, values_only=True), start=2
    ):
        nom, prenom, email, telephone, cursus, sexe, date_naissance, niveau, l, ma, compet, perf = ligne

        if not nom and not prenom and not email:
            continue  # ligne vide

        if not email:
            erreurs.append((i, "email manquant"))
            continue

        email = str(email).strip()
        try:
            validate_email(email)
        except ValidationError:
            erreurs.append((i, f"email invalide : {email}"))
            continue

        if User.objects.filter(email__iexact=email).exists():
            erreurs.append((i, f"email déjà utilisé : {email}"))
            continue

        annee_code = _resoudre_choice(cursus, User.ANNEE_CHOICES)
        if annee_code is None:
            erreurs.append((i, f"cursus inconnu : {cursus}"))
            continue

        sexe_code = _resoudre_choice(sexe, User.SEXE_CHOICES)
        if sexe_code is None:
            erreurs.append((i, f"sexe inconnu : {sexe}"))
            continue

        niveau_code = _resoudre_choice(niveau, User.NIVEAU_CHOICES)
        if niveau_code is None:
            erreurs.append((i, f"niveau inconnu : {niveau}"))
            continue

        date_n = None
        if date_naissance:
            try:
                date_n = _parser_date(date_naissance)
            except ValueError:
                erreurs.append((i, f"date de naissance invalide : {date_naissance}"))
                continue

        candidat = User(
            username=generer_username(prenom or "", nom or ""),
            email=email,
            first_name=(prenom or "").strip(),
            last_name=(nom or "").strip(),
            telephone=normaliser_telephone(telephone) if telephone else "",
            annee=annee_code,
            sexe=sexe_code,
            niveau=niveau_code,
            date_naissance=date_n,
            dispo_lundi=bool(l),
            dispo_mardi=bool(ma),
            dispo_creneaux_compet=bool(compet),
            dispo_creneaux_perf=bool(perf),
        )
        if date_n:
            candidat.set_password(mot_de_passe_initial(date_n))
        else:
            candidat.set_unusable_password()
        candidat.save()
        nb_crees += 1

    return nb_crees, erreurs
