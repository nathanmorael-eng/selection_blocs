from django.contrib import admin

from .models import Ascent, Boulder


@admin.register(Boulder)
class BoulderAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'location')
    search_fields = ('name', 'location')


@admin.register(Ascent)
class AscentAdmin(admin.ModelAdmin):
    list_display = ('user', 'boulder', 'date')
    list_filter = ('user',)
