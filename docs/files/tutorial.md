# Tutorial

This tutorial aims to create a project from the ground up that utilizes the
example code shown in the [README][readme-example]. It assumes that you already
have Django installed.

## Installation

To get started we first need to install the library. This is easily
accomplished using pip:

```bash
pip install django-class-settings
```

Keep in mind that only Django 1.11+ and Python 3.4+ are supported.

## Starting a Project

Before getting started let's also create a new project for the tutorial. We're
going to use Django's startproject command:

```bash
django-admin startproject myproject
```

The resulting layout should look like this:

```
myproject/
    manage.py
    myproject/
        __init__.py
        settings.py
        urls.py
        wsgi.py
```

`myproject/settings.py` is the file we're mostly going to focus on. The next
section assumes that it's empty so let's empty it now.

## Creating the Settings

Now that we've got the library installed and started a project we can get to
the fun part, creating our settings.

First up we need to import the `Settings` class. It will be the foundation we
build our settings on. Open up your `myproject/settings.py` file and import it
like the below:

```python
from class_settings import Settings
```

Next, let's create the actual settings. We're going to subclass the `Settings`
class that we just imported and define all our settings inside of it:

```python
class MySettings(Settings):
    SECRET_KEY = '*2#fz@c0w5fe8f-'
    DEBUG = True
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

For the tutorial, we've only populated our settings with the bare minimum. In
the real world you'd need much more than this, possibly with them even
scattered around in different classes.

## Setting It Up

If you tried to run the server now you would've noticed that an error pops up
talking about the SECRET_KEY setting being empty. What gives? We have it
defined right there under MySettings. Well, Django doesn't actually know that
it's supposed to look in MySettings. It's been searching for it in the
top-level namespace where it doesn't exist, hence the error. Let's fix that by
modifying the `manage.py` file a bit:

```diff
 #!/usr/bin/env python
 import os
 import sys

+import class_settings
+
 if __name__ == '__main__':
     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
+    os.environ.setdefault('DJANGO_SETTINGS_CLASS', 'MySettings')
+    class_settings.setup()
     try:
         from django.core.management import execute_from_command_line
     except ImportError as exc:
         raise ImportError(
             "Couldn't import Django. Are you sure it's installed and "
             "available on your PYTHONPATH environment variable? Did you "
             "forget to activate a virtual environment?"
         ) from exc
     execute_from_command_line(sys.argv)
```

Going through the changes step-by-step:

1. We import the library.
2. We default the DJANGO_SETTINGS_CLASS environment variable to MySettings.
3. We call `setup`.

The last change is where the magic happens. Internally `setup` imports the
module defined in DJANGO_SETTINGS_MODULE, creates an instance of the class
defined in DJANGO_SETTINGS_CLASS, and calls `django.configure` with it. This
lets Django know that our settings are defined in MySettings.

You'd also want to similarly change the `myproject/wsgi.py` file as it's used
instead of `manage.py` for production but I'll leave that as an exercise to the
reader.

## Configuring from the Environment

The setup we have so far is nice but what if you didn't want to hardcode local
settings, such as DATABASES, or if you're going to publish the project to some
kind of public repository, hide sensitive settings, such as SECRET_KEY? You
might've heard a bit about these problems in the config factor of
[The Twelve-Factor App][12factor-config]. Luckily the library provides an
easy-to-use environment variable parser.

Let's begin our _refactor_ by modifying the imports in `myproject/settings.py`:

```diff
-from class_settings import Settings
+from class_settings import Settings, env
```

Say we want to be able to enable DEBUG locally, making it fall back to the
reasonable default of `False` for production, and hide SECRET_KEY from prying
eyes. We'd do that by calling the newly imported `env`:

```diff
 class MySettings(Settings):
-    SECRET_KEY = '*2#fz@c0w5fe8f-'
-    DEBUG = True
+    SECRET_KEY = env()
+    DEBUG = env(default=False)
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

Now we can create a `.env` file with our desired environment:

```bash
export DJANGO_SECRET_KEY='*2#fz@c0w5fe8f-'
export DJANGO_DEBUG=true
```

And then modify `manage.py` to read from it:

```diff
 #!/usr/bin/env python
 import os
 import sys

 import class_settings
+from class_settings import env

 if __name__ == '__main__':
+    env.read_env()
     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
     os.environ.setdefault('DJANGO_SETTINGS_CLASS', 'MySettings')
     class_settings.setup()
     try:
         from django.core.management import execute_from_command_line
     except ImportError as exc:
         raise ImportError(
             "Couldn't import Django. Are you sure it's installed and "
             "available on your PYTHONPATH environment variable? Did you "
             "forget to activate a virtual environment?"
         ) from exc
     execute_from_command_line(sys.argv)
```

And everything should work. This is great but wait, there's a problem. If we
explicitly set DJANGO_DEBUG to `false`, it still acts as if it were set to
`true`. The reason is that we didn't specify that we wanted a boolean. Let's
fix that by modifying our DEBUG like the below:

```diff
-    DEBUG = env(default=False)
+    DEBUG = env.bool(default=False)
```

## Conclusion

Now that the tutorial is over and you've learned the basics you can (hopefully)
apply them to your own project.

[readme-example]: https://github.com/orlnub123/django-class-settings/blob/master/README.md#example
[12factor-config]: https://12factor.net/config
