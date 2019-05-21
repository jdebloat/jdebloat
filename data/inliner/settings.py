from inliner.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))), 'output', 'inliner.sqlite3'),
    }
}
