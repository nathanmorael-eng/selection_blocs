from django.contrib import admin

from .models import Boulder, User
admin.site.register(User)


@admin.register(Boulder)
class BoulderAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'location')
    search_fields = ('name', 'location')



