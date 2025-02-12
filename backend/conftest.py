"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import os
import django
from django.conf import settings
import pytest

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "cad: marks tests that require FreeCAD installation (deselect with '-m \"not cad\"')"
    )
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.contrib.gis.db.backends.postgis',
                'NAME': 'test_eurotempl',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': 'localhost',
                'PORT': '5432',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.gis',
            'core',
            'parameters',
            'cad_engine',
        ],
        USE_TZ=True,
        TIME_ZONE='UTC',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )
    django.setup()