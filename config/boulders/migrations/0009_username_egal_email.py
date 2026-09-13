from django.db import migrations


def synchroniser_username_email(apps, schema_editor):
    User = apps.get_model("boulders", "User")
    for user in User.objects.all():
        if user.username != user.email:
            user.username = user.email
            user.save(update_fields=["username"])


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('boulders', '0008_remove_boulder_grade_boulder_numero'),
    ]

    operations = [
        migrations.RunPython(synchroniser_username_email, reverse_noop),
    ]
