from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImportExcelForm
from .imports import FichierIllisible, importer_excel
from .models import Boulder, Ascent, User
from .vcards import generer_vcf

# whitelist des colonnes triables : on ne fait jamais confiance a une valeur
# venue de l'URL pour construire un order_by() directement
SORT_FIELDS = {"username", "nb_blocs", "niveau", "annee"}

GROUPE_VALUES = {value for value, _ in User.GROUPE_CHOICES}


def organisateur_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_organisateur:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def liste_blocs(request):
    blocs = Boulder.objects.all()
    ids_toppes = set(
        Ascent.objects.filter(user=request.user).values_list("boulder_id", flat=True)
    )
    for bloc in blocs:
        bloc.toppe = bloc.id in ids_toppes  # on attache l'info directement a l'objet

    return render(request, "liste_blocs.html", {"blocs": blocs})


@login_required
def toggle_ascent(request, boulder_id):
    if request.method == "POST":
        boulder = get_object_or_404(Boulder, id=boulder_id)
        ascent = Ascent.objects.filter(user=request.user, boulder=boulder).first()
        if ascent:
            ascent.delete()
        else:
            Ascent.objects.create(user=request.user, boulder=boulder)
    return redirect("liste_blocs")


@organisateur_required
def liste_users(request):
    tri = request.GET.get("tri", "username")
    champ = tri.lstrip("-")
    if champ not in SORT_FIELDS:
        tri = "username"

    # une seule requete pour tout le monde, puis on repartit par groupe en
    # memoire (meme principe que pour ids_toppes dans liste_blocs : on evite
    # de refaire une requete SQL par groupe)
    users = list(User.objects.annotate(nb_blocs=Count("ascents")).order_by(tri))
    # tri Python stable : garde l'ordre ci-dessus, mais fait passer les
    # personnes deja affectees a la fin de la liste
    users.sort(key=lambda u: bool(u.groupe))

    par_groupe = {value: [] for value, _ in User.GROUPE_CHOICES}
    for u in users:
        if u.groupe in par_groupe:
            par_groupe[u.groupe].append(u)

    return render(request, "liste_users.html", {
        "users": users,
        "tri_actuel": tri,
        "affectes_compet": par_groupe["compet"],
        "affectes_perf": par_groupe["perf"],
        "affectes_refuse": par_groupe["refuse"],
        "nb_compet": len(par_groupe["compet"]),
        "nb_perf": len(par_groupe["perf"]),
    })


@organisateur_required
def affecter_groupe(request, user_id):
    if request.method != "POST":
        return redirect("liste_users")

    groupe = request.POST.get("groupe")
    if groupe not in GROUPE_VALUES:
        return HttpResponseBadRequest("groupe invalide")

    candidat = get_object_or_404(User, id=user_id)
    candidat.groupe = groupe
    candidat.save()
    messages.success(request, f"{candidat.first_name} {candidat.last_name} affecté(e) au groupe {candidat.get_groupe_display()}")
    return redirect("liste_users")


@organisateur_required
def retirer_affectation(request, user_id):
    if request.method != "POST":
        return redirect("liste_users")

    candidat = get_object_or_404(User, id=user_id)
    candidat.groupe = ""
    candidat.save()
    messages.success(request, f"Affectation retirée pour {candidat.first_name} {candidat.last_name}")
    return redirect("liste_users")


@organisateur_required
def import_excel(request):
    if request.method == "POST":
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                nb_crees, erreurs = importer_excel(form.cleaned_data["fichier"])
            except FichierIllisible as e:
                messages.error(request, str(e))
            else:
                messages.success(request, f"{nb_crees} utilisateur(s) créé(s).")
                for ligne, raison in erreurs:
                    messages.warning(request, f"Ligne {ligne} ignorée : {raison}")
                return redirect("liste_users")
    else:
        form = ImportExcelForm()

    return render(request, "import_excel.html", {"form": form})


@organisateur_required
def contacts_vcf(request):
    candidats_compet = User.objects.filter(groupe="compet").order_by("last_name", "first_name")
    candidats_perf = User.objects.filter(groupe="perf").order_by("last_name", "first_name")
    contenu = generer_vcf(candidats_compet, candidats_perf)

    response = HttpResponse(contenu, content_type="text/vcard")
    response["Content-Disposition"] = 'attachment; filename="contacts_compet_perf.vcf"'
    return response

