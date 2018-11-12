# django-class-settings

[![pypi-image]][pypi-url]
[![django-version-image]][pypi-url]
[![python-version-image]][pypi-url]
[![license-image]][license-url]
[![code-style-image]][code-style-url]

django-class-settings aims to simplify complicated settings layouts by using
classes instead of modules. Some of the benefits of using classes include:
- Real inheritance
- [Foolproof settings layouts][local_settings]
- Properties
- Implicit environment variable names

## Example

```python
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

**Requirements:**
- Django 1.11+
- Python 3.4+

## Resources

- Releases: https://pypi.org/project/django-class-settings/
- Code: https://github.com/orlnub123/django-class-settings
- License: [MIT][license-url]

[code-style-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[code-style-url]: https://github.com/ambv/black
[django-version-image]: https://img.shields.io/pypi/djversions/django-class-settings.svg
[license-image]: https://img.shields.io/pypi/l/django-class-settings.svg
[license-url]: https://github.com/orlnub123/django-class-settings/blob/master/LICENSE
[local_settings]: https://www.pydanny.com/using-executable-code-outside-version-control.html
[pip-url]: https://pip.pypa.io/en/stable/quickstart/
[pypi-image]: https://img.shields.io/pypi/v/django-class-settings.svg
[pypi-url]: https://pypi.org/project/django-class-settings/
[python-version-image]: https://img.shields.io/pypi/pyversions/django-class-settings.svg
