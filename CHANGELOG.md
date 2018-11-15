# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - Unreleased

### Added

- Added `Env.read_env` to read into the environment from a .env file.

## [0.1.1] - Unreleased

### Fixed

- Fixed nested `Env.prefixed` context managers with lowercase prefixes not
  having `_` appended to their prefixes.
- Fixed exceptions not being correctly chained.
- Made sure DJANGO_SETTINGS_CLASS points to a Settings subclass.

## [0.1.0] - 2018-11-13

Initial release.

[0.2.0]: https://github.com/orlnub123/django-class-settings/compare/0.1.0...master
[0.1.1]: https://github.com/orlnub123/django-class-settings/compare/0.1.0...release/0.1
[0.1.0]: https://github.com/orlnub123/django-class-settings/releases/tag/0.1.0
