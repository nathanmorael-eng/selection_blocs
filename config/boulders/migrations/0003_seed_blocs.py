from django.db import migrations


def create_blocs(apps, schema_editor):
    Boulder = apps.get_model("boulders", "Boulder")
    Boulder.objects.bulk_create([
        Boulder(name=f"bloc {i}") for i in range(1, 22)
    ])


def delete_blocs(apps, schema_editor):
    Boulder = apps.get_model("boulders", "Boulder")
    names = [f"bloc {i}" for i in range(1, 22)]
    Boulder.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('boulders', '0002_ascent'),
    ]

    operations = [
        migrations.RunPython(create_blocs, delete_blocs),
    ]
