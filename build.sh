#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

cd CarWashPOS

python manage.py collectstatic --no-input

# Recovery: if core.0002_remove_calendarevent was applied before the FK update
# migrations existed (from a previous deploy), fake-unapply it so that migrate
# can re-apply everything in the correct dependency order.
# This is a no-op on a fresh database or when the state is already consistent.
python manage.py shell << 'PYEOF'
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM django_migrations "
            "WHERE app='core' AND name='0002_remove_calendarevent'"
        )
        core_002_applied = cursor.fetchone()[0] > 0

        cursor.execute(
            "SELECT COUNT(*) FROM django_migrations "
            "WHERE app='salaries' AND name='0002_update_salary_date_fk'"
        )
        salaries_002_applied = cursor.fetchone()[0] > 0

        if core_002_applied and not salaries_002_applied:
            cursor.execute(
                "DELETE FROM django_migrations "
                "WHERE app='core' AND name IN "
                "('0002_remove_calendarevent', '0003_alter_employee_employee_id')"
            )
            print("Migration recovery: removed stale core.0002 / core.0003 entries.")
        else:
            print("Migration state is consistent — no recovery needed.")
except Exception as e:
    print(f"Migration recovery check skipped: {e}")
PYEOF

python manage.py migrate
