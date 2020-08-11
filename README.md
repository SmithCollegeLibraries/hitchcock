Hitchcock is a web application for managing and providing access to electronic reserves materials.

# Setup
Requires Python 3.5 or later. 

For a local development environment:

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
patches/apply_patches.sh

# You must specify the settings file before running Django e.g.
export DJANGO_SETTINGS_MODULE=hitchcock.settings.local_tristan

python manage.py runserver
```

To make a new settings file:

``` bash
cp src/hitchcock/settings/local_tristan.py src/hitchcock/settings/local_me.py
# ... edit src/hitchcock/settings/local_me.py ...
export DJANGO_SETTINGS_MODULE=hitchcock.settings.local_me
```
