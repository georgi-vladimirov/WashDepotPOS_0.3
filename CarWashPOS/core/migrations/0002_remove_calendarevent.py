from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("cal_app", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="CalendarEvent"),
            ],
            database_operations=[],
        ),
    ]
