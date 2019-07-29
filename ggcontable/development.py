# Django settings for sistema_bomberos project.
from .settings import *


DEBUG = True
# DEBUG = False

TEMPLATE_DEBUG = DEBUG


MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',#Barra DEBUG
)



INSTALLED_APPS += (
    'debug_toolbar',    
)



# BOOTSTRAP3 = {

#     # The Bootstrap base URL
#     'base_url': os.path.join(SITE_ROOT, 'staticfiles/css/'),

#     # The complete URL to the Bootstrap CSS file (None means derive it from base_url)
#     'css_url': None,

#     # The complete URL to the Bootstrap CSS file (None means no theme)
#     'theme_url': None,

#     # The complete URL to the Bootstrap JavaScript file (None means derive it from base_url)
#     'javascript_url': None,

#     # Put JavaScript in the HEAD section of the HTML document (only relevant if you use bootstrap3.html)
#     'javascript_in_head': False,

#     # Include jQuery with Bootstrap JavaScript (affects django-bootstrap3 template tags)
#     'include_jquery': False,

#     # Label class to use in horizontal forms
#     'horizontal_label_class': 'col-md-2',

#     # Field class to use in horizontal forms
#     'horizontal_field_class': 'col-md-5',

#     # Set HTML required attribute on required fields
#     'set_required': True,

#     # Set HTML disabled attribute on disabled fields
#     'set_disabled': False,

#     # Set placeholder attributes to label if no placeholder is provided
#     'set_placeholder': True,

#     # Class to indicate required (better to set this in your Django form)
#     'required_css_class': '',

#     # Class to indicate error (better to set this in your Django form)
#     'error_css_class': 'has-error',

#     # Class to indicate success, meaning the field has valid input (better to set this in your Django form)
#     'success_css_class': 'has-success',


# }
