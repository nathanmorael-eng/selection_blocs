from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="liste_blocs", permanent=False)),
    path("blocs/", views.liste_blocs, name="liste_blocs"),
    path("blocs/<int:boulder_id>/toggle/", views.toggle_ascent, name="toggle_ascent"),
    path("blocs/gerer/", views.gerer_blocs, name="gerer_blocs"),
    path("blocs/<int:boulder_id>/supprimer/", views.supprimer_bloc, name="supprimer_bloc"),
    path("users/", views.liste_users, name="liste_users"),
    path("users/ajouter/", views.ajouter_user, name="ajouter_user"),
    path("users/import/", views.import_excel, name="import_excel"),
    path("users/contacts.vcf", views.contacts_vcf, name="contacts_vcf"),
    path("users/<int:user_id>/affecter/", views.affecter_groupe, name="affecter_groupe"),
    path("users/<int:user_id>/retirer/", views.retirer_affectation, name="retirer_affectation"),
    path("users/<int:user_id>/supprimer/", views.supprimer_user, name="supprimer_user"),
    path("users/supprimer-non-organisateurs/", views.supprimer_tous_non_organisateurs, name="supprimer_tous_non_organisateurs"),
]