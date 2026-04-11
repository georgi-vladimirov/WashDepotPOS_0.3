import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cal_app", "0001_initial"),
        ("transactions", "0002_transaction_details"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="transaction",
                    name="date",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="cal_app.calendarevent",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
