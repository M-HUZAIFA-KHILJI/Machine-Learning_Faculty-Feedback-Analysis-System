web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn professor_feedback.wsgi:application --workers 3 --bind 0.0.0.0:$PORT
