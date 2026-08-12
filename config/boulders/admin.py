from django.contrib import admin
from django.db.models import Count

from .models import Boulder, User
from .utils import mot_de_passe_initial


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'niveau', 'annee', 'nb_blocs')
    list_filter = ('niveau', 'annee', 'sexe')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    # le mot de passe ne doit jamais etre saisi/affiche en clair dans ce formulaire :
    # il est derive automatiquement de la date de naissance a la creation (voir save_model)
    exclude = ('password',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(nb_blocs=Count('ascents'))

    @admin.display(description='Blocs toppés', ordering='nb_blocs')
    def nb_blocs(self, obj):
        return obj.nb_blocs

    def save_model(self, request, obj, form, change):
        if not change:
            if obj.date_naissance:
                obj.set_password(mot_de_passe_initial(obj.date_naissance))
            else:
                obj.set_unusable_password()
        super().save_model(request, obj, form, change)


@admin.register(Boulder)
class BoulderAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'location')
    search_fields = ('name', 'location')



