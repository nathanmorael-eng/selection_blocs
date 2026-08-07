from django.conf import settings
from django.db import models


class Boulder(models.Model):
    name = models.CharField(max_length=200)
    grade = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Ascent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ascents')
    boulder = models.ForeignKey(Boulder, on_delete=models.CASCADE, related_name='ascents')
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'boulder')

    def __str__(self):
        return f'{self.user} - {self.boulder}'
