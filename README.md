Hitchcock is a web application for managing and providing access to locally hosted electronic reserves materials.

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

In a production setting you will probably want to set the configuration in the
wsgi.py file, instead of via the environment variable. Like this:

``` python
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hitchcock.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hitchcock.settings.ereserves')
```
## Trouble shooting

If you try to run `manage.py` and get this error:

```
...
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
```

It's because you didn't set the settings environment variable. Sett above.
