def mot_de_passe_initial(date_naissance):
    return date_naissance.strftime("%d%m%Y")


def normaliser_telephone(valeur):
    texte = str(valeur).strip()
    if not texte:
        return ""
    return texte if texte.startswith("+") else f"+{texte}"
