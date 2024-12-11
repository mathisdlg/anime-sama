FROM python:3.11

WORKDIR /app

RUN pip install requests beautifulsoup4 pycurl django django-bootstrap5 gunicorn

COPY . .

ENV RUN_MODE=WEB

EXPOSE 8000

CMD ["sh", "-c", "if [ \"$RUN_MODE\" = \"TUI\" ]; then python manage.py shell; else gunicorn anime_sama.wsgi:application --bind 0.0.0.0:8000; fi"]
