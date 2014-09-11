
from settings import *

DEBUG = TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'partsms', 
        'HOST': '127.0.0.1', 
        'USER': 'jcchen', 
        'PASSWORD': 'jcchen',
        'PORT': '3306', 
    }
}

ALLOWED_HOSTS = ['127.0.0.1','diskspc2.itp.com',]

ADMINS = (
    ('Junchang Chen', 'junchang.chen@hgst.com'), 
)

MANAGERS = (
    ('Junchang Chen', 'junchang.chen@hgst.com'), 
)

