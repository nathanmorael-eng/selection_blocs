from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="liste_blocs", permanent=False)),
    path("blocs/", views.liste_blocs, name="liste_blocs"),
    path("blocs/<int:boulder_id>/toggle/", views.toggle_ascent, name="toggle_ascent"),
    path("users/", views.liste_users, name="liste_users"),
    path("users/import/", views.import_excel, name="import_excel"),
    path("users/contacts.vcf", views.contacts_vcf, name="contacts_vcf"),
    path("users/<int:user_id>/affecter/", views.affecter_groupe, name="affecter_groupe"),
    path("users/<int:user_id>/retirer/", views.retirer_affectation, name="retirer_affectation"),
]