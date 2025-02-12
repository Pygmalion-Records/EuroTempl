"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import os
import django
from django.conf import settings

def pytest_configure():
    
    django.setup()