from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="liste_blocs", permanent=False)),
    path("blocs/", views.liste_blocs, name="liste_blocs"),
    path("blocs/<int:boulder_id>/toggle/", views.toggle_ascent, name="toggle_ascent"),
]