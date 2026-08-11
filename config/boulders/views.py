from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Boulder, Ascent

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


