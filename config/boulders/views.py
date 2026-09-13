from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AjouterUserForm, BoulderForm, ImportExcelForm
from .imports import FichierIllisible, importer_excel
from .models import Boulder, Ascent, User
from .utils import mot_de_passe_initial
from .vcards import generer_vcf

# whitelist des colonnes triables : on ne fait jamais confiance a une valeur
# venue de l'URL pour construire un order_by() directement
SORT_FIELDS = {"username", "nb_blocs", "niveau", "annee", "sexe"}

# pour certains tris, on ajoute un critere secondaire (ex: a sexe egal, on
# affiche d'abord ceux qui ont toppe le plus de blocs)
SORT_SECONDAIRE = {
    "sexe": ["sexe", "-nb_blocs"],
    "-sexe": ["-sexe", "-nb_blocs"],
}

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
    blocs = list(Boulder.objects.order_by("numero"))
    ids_toppes = set(
        Ascent.objects.filter(user=request.user).values_list("boulder_id", flat=True)
    )
    for bloc in blocs:
        bloc.toppe = bloc.id in ids_toppes  # on attache l'info directement a l'objet

    return render(request, "liste_blocs.html", {
        "blocs": blocs,
        "nb_total": len(blocs),
        "nb_toppes": sum(1 for b in blocs if b.toppe),
    })


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
    q = request.GET.get("q", "").strip()

    # une seule requete pour tout le monde, puis on repartit par groupe et on
    # filtre par recherche en memoire (meme principe que pour ids_toppes dans
    # liste_blocs : on evite de refaire une requete SQL par groupe/recherche)
    ordre = SORT_SECONDAIRE.get(tri, [tri])
    users = list(User.objects.annotate(nb_blocs=Count("ascents")).order_by(*ordre))
    # tri Python stable : garde l'ordre ci-dessus, mais fait passer les
    # personnes deja affectees a la fin de la liste
    users.sort(key=lambda u: bool(u.groupe))

    par_groupe = {value: [] for value, _ in User.GROUPE_CHOICES}
    for u in users:
        if u.groupe in par_groupe:
            par_groupe[u.groupe].append(u)

    if q:
        q_lower = q.lower()
        users_affiches = [
            u for u in users
            if q_lower in u.username.lower()
            or q_lower in u.first_name.lower()
            or q_lower in u.last_name.lower()
            or q_lower in u.email.lower()
        ]
    else:
        users_affiches = users

    return render(request, "liste_users.html", {
        "users": users_affiches,
        "tri_actuel": tri,
        "q": q,
        "affectes_compet": par_groupe["compet"],
        "affectes_perf": par_groupe["perf"],
        "affectes_refuse": par_groupe["refuse"],
        "nb_compet": len(par_groupe["compet"]),
        "nb_perf": len(par_groupe["perf"]),
    })


@organisateur_required
def supprimer_user(request, user_id):
    if request.method != "POST":
        return redirect("liste_users")

    if user_id == request.user.id:
        messages.error(request, "Tu ne peux pas te supprimer toi-même.")
        return redirect("liste_users")

    candidat = get_object_or_404(User, id=user_id)
    messages.success(request, f"{candidat.first_name} {candidat.last_name} supprimé(e).")
    candidat.delete()
    return redirect("liste_users")


@organisateur_required
def supprimer_tous_non_organisateurs(request):
    if request.method != "POST":
        return redirect("liste_users")

    nb = User.objects.filter(is_organisateur=False).count()
    User.objects.filter(is_organisateur=False).delete()
    messages.success(request, f"{nb} utilisateur(s) non-organisateur(s) supprimé(s).")
    return redirect("liste_users")


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


@organisateur_required
def ajouter_user(request):
    if request.method == "POST":
        form = AjouterUserForm(request.POST)
        if form.is_valid():
            candidat = form.save(commit=False)
            candidat.username = candidat.email
            if candidat.date_naissance:
                candidat.set_password(mot_de_passe_initial(candidat.date_naissance))
            else:
                candidat.set_unusable_password()
            candidat.save()
            messages.success(request, f"{candidat.first_name} {candidat.last_name} ajouté(e) (identifiant : {candidat.username}).")
            return redirect("liste_users")
    else:
        form = AjouterUserForm()

    return render(request, "ajouter_user.html", {"form": form})


@organisateur_required
def gerer_blocs(request):
    if request.method == "POST":
        form = BoulderForm(request.POST)
        if form.is_valid():
            bloc = form.save()
            messages.success(request, f"Bloc « {bloc.name} » ajouté.")
            return redirect("gerer_blocs")
    else:
        form = BoulderForm()

    blocs = Boulder.objects.all().order_by("numero")
    return render(request, "gerer_blocs.html", {"form": form, "blocs": blocs})


@organisateur_required
def supprimer_bloc(request, boulder_id):
    if request.method != "POST":
        return redirect("gerer_blocs")

    bloc = get_object_or_404(Boulder, id=boulder_id)
    bloc.delete()
    messages.success(request, f"Bloc « {bloc.name} » supprimé.")
    return redirect("gerer_blocs")

