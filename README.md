# Physics Wallah - Student Authentication System

# 1. Create virtual environment
python -m venv venv

# 2. Activate it
source venv/Scripts/activate      # Git Bash on Windows

# 3. Install all packages
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (optional)
python manage.py createsuperuser




# 6. Run server
python manage.py runserver