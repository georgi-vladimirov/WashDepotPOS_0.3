import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="CalendarEvent",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("is_active", models.BooleanField(default=True)),
                        ("date_created", models.DateTimeField(auto_now_add=True)),
                        ("date_modified", models.DateTimeField(auto_now=True)),
                        ("date", models.DateField()),
                        (
                            "location",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to="core.location",
                                unique_for_date="date",
                            ),
                        ),
                    ],
                    options={"unique_together": {("date", "location")}},
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM pg_tables
                                WHERE schemaname = 'public'
                                AND tablename = 'core_calendarevent'
                            ) THEN
                                ALTER TABLE "core_calendarevent" RENAME TO "cal_app_calendarevent";
                            END IF;
                        END $$;
                    """,
                    reverse_sql="""
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM pg_tables
                                WHERE schemaname = 'public'
                                AND tablename = 'cal_app_calendarevent'
                            ) THEN
                                ALTER TABLE "cal_app_calendarevent" RENAME TO "core_calendarevent";
                            END IF;
                        END $$;
                    """,
                ),
            ],
        ),
    ]
