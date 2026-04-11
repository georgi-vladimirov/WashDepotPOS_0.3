import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cal_app", "0001_initial"),
        ("expences", "0002_alter_expence_transaction"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="expence",
                    name="date",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expences",
                        to="cal_app.calendarevent",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
