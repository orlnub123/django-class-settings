# django-class-settings

[![pypi][pypi-image]][pypi-url]
[![django versions][django-version-image]][pypi-url]
[![python][python-version-image]][pypi-url]
[![build][travis-image]][travis-url]
[![coverage][coverage-image]][coverage-url]
[![license][license-image]][license-url]
[![code style][code-style-image]][code-style-url]

django-class-settings aims to simplify complicated settings layouts by using
classes instead of modules. Some of the benefits of using classes include:

- Real inheritance
- [Foolproof settings layouts][local_settings]
- Properties
- Implicit environment variable names

## Example

```bash
# .env
export DJANGO_SECRET_KEY='*2#fz@c0w5fe8f-'
export DJANGO_DEBUG=true
```

```python
# manage.py
import os
import sys

import class_settings
from class_settings import env

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    env.read_env()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    os.environ.setdefault('DJANGO_SETTINGS_CLASS', 'MySettings')
    class_settings.setup()
    execute_from_command_line(sys.argv)
```

```python
# myproject/settings.py
from class_settings import Settings, env


class MySettings(Settings):
    SECRET_KEY = env()
    DEBUG = env.bool(default=False)
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]
    ROOT_URLCONF = 'myproject.urls'
    WSGI_APPLICATION = 'myproject.wsgi.application'
```

## Installation

Install it from [PyPI][pypi-url] with [pip][pip-url]:

```bash
pip install django-class-settings
```

### Requirements

- Django 1.11+
- Python 3.5+

## Resources

- Documentation: https://django-class-settings.readthedocs.io/
- Releases: https://pypi.org/project/django-class-settings/
- Changelog: https://github.com/orlnub123/django-class-settings/blob/master/CHANGELOG.md
- Code: https://github.com/orlnub123/django-class-settings
- License: [MIT][license-url]

[code-style-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[code-style-url]: https://github.com/ambv/black
[coverage-image]: https://img.shields.io/codecov/c/gh/orlnub123/django-class-settings.svg
[coverage-url]: https://codecov.io/gh/orlnub123/django-class-settings
[django-version-image]: https://img.shields.io/pypi/djversions/django-class-settings.svg
[license-image]: https://img.shields.io/pypi/l/django-class-settings.svg
[license-url]: https://github.com/orlnub123/django-class-settings/blob/master/LICENSE
[local_settings]: https://www.pydanny.com/using-executable-code-outside-version-control.html
[pip-url]: https://pip.pypa.io/en/stable/quickstart/
[pypi-image]: https://img.shields.io/pypi/v/django-class-settings.svg
[pypi-url]: https://pypi.org/project/django-class-settings/
[python-version-image]: https://img.shields.io/pypi/pyversions/django-class-settings.svg
[travis-image]: https://img.shields.io/travis/orlnub123/django-class-settings.svg
[travis-url]: https://travis-ci.org/orlnub123/django-class-settings
