#!/bin/bash

# Ejecutar migraciones
python manage.py migrate --no-input

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Iniciar Gunicorn
gunicorn l_atelier.wsgi:application
