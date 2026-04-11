import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cal_app", "0001_initial"),
        ("sales", "0003_alter_sale_manager_alter_sale_subscriber_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="sale",
                    name="date",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sales",
                        to="cal_app.calendarevent",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
