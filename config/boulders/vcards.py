def _carte(nom_contact, telephone):
    return (
        "BEGIN:VCARD\r\n"
        "VERSION:3.0\r\n"
        f"FN:{nom_contact}\r\n"
        f"N:;{nom_contact};;;\r\n"
        f"TEL;TYPE=CELL:{telephone}\r\n"
        "END:VCARD\r\n"
    )


def generer_vcf(candidats_compet, candidats_perf):
    """Cree un fichier .vcf (cartes de contact) : un contact par candidat avec
    telephone, nomme prefixe_i (compet_1, compet_2, ..., perf_1, perf_2, ...).
    Les candidats sans telephone renseigne sont ignores (carte inutile sans numero)."""
    cartes = []
    for i, candidat in enumerate(candidats_compet, start=1):
        if candidat.telephone:
            cartes.append(_carte(f"compet_{i}", candidat.telephone))
    for i, candidat in enumerate(candidats_perf, start=1):
        if candidat.telephone:
            cartes.append(_carte(f"perf_{i}", candidat.telephone))
    return "".join(cartes)
