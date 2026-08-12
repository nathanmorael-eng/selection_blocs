import unicodedata

from .models import User


def mot_de_passe_initial(date_naissance):
    return date_naissance.strftime("%d%m%Y")


def generer_username(prenom, nom):
    base = unicodedata.normalize("NFKD", f"{prenom}.{nom}").encode("ascii", "ignore").decode().lower()
    base = "".join(c for c in base if c.isalnum() or c == ".") or "membre"
    username = base
    i = 1
    while User.objects.filter(username=username).exists():
        i += 1
        username = f"{base}{i}"
    return username


def normaliser_telephone(valeur):
    texte = str(valeur).strip()
    if not texte:
        return ""
    return texte if texte.startswith("+") else f"+{texte}"
