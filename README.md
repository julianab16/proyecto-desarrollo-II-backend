# proyecto-desarrollo-II-backend

Breve descripción
- Backend Django REST para el proyecto Desarrollo II.

Requisitos
- Python 3.11+
- PostgreSQL 
- Docker (opcional para servicios como SonarQube/Postgres)
- Node/Frontend separado (si aplica)

Instalación (Windows — PowerShell)
```powershell
# Crear y activar virtualenv
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
& .\.venv\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Configuración de entorno
- Crear `.env` en la raíz (no subirlo al repo). Ejemplo:
```
SECRET_KEY=tu_secret_key_local
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

Migraciones y ejecución
```powershell
python manage.py migrate
python manage.py runserver
# o para pruebas locales con postgres usar DATABASE_URL o variables en .env
```

Tests y cobertura
```powershell
# Ejecutar tests con pytest + cobertura
$env:DJANGO_SETTINGS_MODULE='l_atelier.settings'
python -m pytest --cov=apps --cov-report=xml:coverage.xml --cov-report=term -q
# Alternativa con coverage + manage.py
python -m coverage run --source='apps' manage.py test apps --keepdb
python -m coverage xml -o coverage.xml
```


CI / SonarQube

- El repo incluye `.github/workflows/django.yml` y `sonar-project.properties`.  
- GitHub Actions generará `coverage.xml` y ejecutará Sonar/linters según la configuración.

Contribuir
- Crear rama descriptiva: `git checkout -b feature/mi-cambio`
- Commit y push: `git push -u origin feature/mi-cambio`
- Abrir PR y esperar CI.
