#!/bin/sh

# Exit on error
set -e

echo "Waiting for Postgres to be ready (using /dev/tcp)..."
until pg_isready -h db -U "$POSTGRES_USER" -d postgres; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done
echo "Postgres is up and running!"

echo "Applying database migrations..."
python manage.py migrate

# Check if superuser exists, if not, create one
# echo "Creating superuser if not exists..."
# python manage.py shell <<EOF
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username="admin").exists():
#     User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
#     print("Superuser created.")
# else:
#     print("Superuser already exists.")
# EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput

python manage.py import_csv_files

echo "Starting Django server..."
exec "$@"
