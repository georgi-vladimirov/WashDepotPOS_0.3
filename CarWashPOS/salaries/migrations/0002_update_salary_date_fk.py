import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cal_app", "0001_initial"),
        ("core", "0002_remove_calendarevent"),
        ("salaries", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="salary",
                    name="date",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="salaries",
                        to="cal_app.calendarevent",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
