
from core_settings import *

SECRET_KEY = 'xz#=4k+4we__68ge_i6v_e5v^+km*p+j=+8qjcq(ox%qle!@k*'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}