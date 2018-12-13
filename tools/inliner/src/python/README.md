# README

## Setup

1. Create a python virtual environment with:
       cd src/python
       python -m venv venv
2. (Optional) Copy the database to this directory: `db.sqlite3`.
3. Activate the virtual environment with: `source venv/bin/activate`.
4. Install dependencies with: `pip install -r requirements.txt`.
5. Migrate the database (if not copied in step 2): `python manage.py migrate`.

You'll now be able to browse the database with `python manage.py runserver`
and navigating to `http://localhost:8000`. If you want to explore the database
with the shell use `python manage.py shell` and as the first command import
the models with `from logcompilation.models import *`.
