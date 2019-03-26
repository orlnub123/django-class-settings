# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - Unreleased

### Added

- Added `Env.read_env` to read into the environment from a .env file.
- Added the `optional` env argument that defaults to acting as a noop.
- Made the default settings accessible directly from the class.
- Allowed `None` to be passed as a prefix.

## [0.1.3] - Unreleased

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

[0.2.0]: https://github.com/orlnub123/django-class-settings/compare/0.1.0...master
[0.1.3]: https://github.com/orlnub123/django-class-settings/compare/0.1.2...release/0.1
[0.1.2]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.2
[0.1.1]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.1
[0.1.0]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.0
