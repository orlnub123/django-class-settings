# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] - Unreleased

## [0.2.1] - Unreleased

## [0.2.0] - 2020-01-03

### Added

- Added `Env.read_env` to read into the environment from a .env file.
- Added the `optional` env argument that defaults to acting as a noop.
- Made the default settings accessible directly from the class.
- Allowed `None` to be passed as a prefix.
- Added the inject_settings Meta option to inject inherited settings into the
  class namespace.

### Changed

- Excluded nonupper attributes from default_settings.
- Restricted the settings module to the {module}:{class} formatting.
- Stopped normalizing lowercase prefixes.

### Fixed

- Fixed Settings subclasses not inheriting the correct Meta sometimes.

## [0.1.3] - 2019-12-25

### Fixed

- Ensured Meta is a class.
- Fixed `Env.prefixed` not resetting the prefix on exceptions.
- Fixed misleading missing environment variable error messages.
- Fixed lowercase prefixes not being normalized to uppercase.

## [0.1.2] - 2019-03-17

### Fixed

- Fixed indented Settings subclasses erroring.
- Fixed `Settings.is_overridden` ignoring class attributes.

## [0.1.1] - 2018-11-20

### Fixed

- Fixed nested `Env.prefixed` context managers with lowercase prefixes not
  having `_` appended to their prefixes.
- Fixed exceptions not being correctly chained.
- Made sure DJANGO_SETTINGS_CLASS points to a Settings subclass.
- Fixed prefixless env calls erroring outside of Settings subclasses.

## [0.1.0] - 2018-11-13

Initial release.

[0.3.0]: https://github.com/orlnub123/django-class-settings/compare/0.2.0...master
[0.2.1]: https://github.com/orlnub123/django-class-settings/compare/0.2.0...release/0.2
[0.2.0]: https://github.com/orlnub123/django-class-settings/releases/tag/0.2.0
[0.1.3]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.3
[0.1.2]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.2
[0.1.1]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.1
[0.1.0]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.0
