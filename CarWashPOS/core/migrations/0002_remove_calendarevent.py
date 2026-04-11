from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("cal_app", "0001_initial"),
        ("sales", "0004_update_sale_date_fk"),
        ("transactions", "0003_update_transaction_date_fk"),
        ("expences", "0003_update_expence_date_fk"),
        ("salaries", "0002_update_salary_date_fk"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="CalendarEvent"),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql='DROP TABLE IF EXISTS "core_calendarevent"',
                    reverse_sql="",
                ),
            ],
        ),
    ]
