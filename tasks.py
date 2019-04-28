import functools
import inspect
import re
import sys
from datetime import datetime

from invoke import task


def get_version():
    with open("class_settings/__init__.py") as f:
        return re.search(
            r"""^[ \t]*__version__[ \t]*=[ \t]*['"](.*?)['"]""",
            f.read(),
            flags=re.MULTILINE,
        )[1]


def update_version(c, version):
    # Update pyproject.toml version
    c.run(f"poetry version {version}", hide="out")
    # Update __version__
    with open("class_settings/__init__.py", "r+") as f:
        content = re.sub(
            r"""^([ \t]*__version__[ \t]*=[ \t]*['"]).*?(['"])""",
            fr"\g<1>{version}\2",
            f.read(),
            flags=re.MULTILINE,
        )
        f.seek(0)
        f.write(content)
        f.truncate()


def check_git(func):
    @functools.wraps(func)
    def wrapper(c, *args, **kwargs):
        branch = c.run("git rev-parse --abbrev-ref HEAD", hide="out").stdout.strip()
        if branch == "HEAD":
            sys.exit(f"Cannot {func.__name__} while in a detached HEAD! Aborting.")
        if branch != "master" and not branch.startswith("release/"):
            sys.exit(f"On unknown branch {branch!r}! Aborting.")
        if c.run("git diff-index --quiet HEAD", warn=True).failed:
            sys.exit("There are uncommited changes! Aborting.")
        return func(c, *args, **kwargs)

    # Fool invoke into thinking the wrapper takes the same options as the func
    wrapper.__signature__ = inspect.signature(func)
    return wrapper


class Releaser:
    def __init__(self, context):
        self.c = context
        self.version = get_version()
        self.release_version = self.version.rstrip("-dev")

    def update_changelog(self):
        self._update_changelog_date()
        self._update_changelog_link()

    def _update_changelog_date(self):
        with open("CHANGELOG.md", "r+") as f:
            escaped_version = re.escape(self.release_version)
            content = re.sub(
                fr"^([ \t]*#+[ \t]*\[{escaped_version}\] - )Unreleased$",
                fr"\g<1>{datetime.utcnow().date().isoformat()}",
                f.read(),
                flags=re.MULTILINE,
            )
            f.seek(0)
            f.write(content)
            f.truncate()

    def _update_changelog_link(self):
        with open("CHANGELOG.md", "r+") as f:
            base = "https://github.com/orlnub123/django-class-settings/releases"
            escaped_version = re.escape(self.release_version)
            content = re.sub(
                fr"^([ \t]*\[{escaped_version}\]:[ \t]*).+",
                fr"\1{base}/tag/{self.release_version}",
                f.read(),
                flags=re.MULTILINE,
            )
            f.seek(0)
            f.write(content)
            f.truncate()

    def update_version(self):
        update_version(self.c, self.release_version)


class Bumper:
    def __init__(self, context, bump):
        self.c = context
        self.version = get_version()
        self.release_version = self.c.run(
            f"poetry version {bump}", hide="out"
        ).stdout.rsplit(maxsplit=1)[1]
        self.bump_version = self.release_version + "-dev"
        self.current_branch = self.c.run(
            "git rev-parse --abbrev-ref HEAD"
        ).stdout.strip()

    def update_version(self):
        update_version(self.c, self.bump_version)

    def update_changelog(self):
        self._add_changelog_stub()
        self._add_changelog_link()

    def _add_changelog_stub(self):
        with open("CHANGELOG.md", "r+") as f:
            content = re.sub(
                fr"^([ \t]*#+[ \t]*)\[{re.escape(self.version)}\] - .+",
                fr"\1[{self.release_version}] - Unreleased\n\n\g<0>",
                f.read(),
                flags=re.MULTILINE,
            )
            f.seek(0)
            f.write(content)
            f.truncate()

    def _add_changelog_link(self):
        with open("CHANGELOG.md", "r+") as f:
            base = "https://github.com/orlnub123/django-class-settings/compare"
            content = re.sub(
                fr"^([ \t]*)\[{re.escape(self.version)}\]:([ \t]*).+",
                fr"\1[{self.release_version}]:\2"
                fr"{base}/{self.version}...{self.current_branch}\n\g<0>",
                f.read(),
                flags=re.MULTILINE,
            )
            f.seek(0)
            f.write(content)
            f.truncate()


@task
def format(c):
    c.run("isort -rc .")
    c.run("black .")


@task
def lint(c):
    commands = ["flake8 .", "isort -rc -c -q .", "black --check -q ."]
    if any(c.run(command, warn=True).failed for command in commands):
        sys.exit(1)


@task
def test(c, all=False, report=False):
    if all:
        c.run("coverage erase")
        c.run("tox -p auto -- --cov --cov-report= --cov-append .", pty=True)
    else:
        c.run("pytest --cov --cov-report= .", pty=True)
    if report:
        c.run("coverage report")


@task
@check_git
def backport(c, commit):
    current_branch = c.run("git rev-parse --abbrev-ref HEAD").stdout.strip()
    if current_branch == "master":
        sys.exit("Cannot backport from master. Did you switch branches?")
    c.run(f"git cherry-pick -x {commit}")
    message = c.run("git log --format=%B -n 1").stdout.strip()
    subject_prefix = f"[{current_branch[len('release/') :]}]"
    c.run(f"git commit --amend -m '{subject_prefix} {message}'")


@task
@check_git
def release(c, publish=False, bump=""):
    releaser = Releaser(c)
    if not releaser.version.endswith("-dev"):
        sys.exit("Current version isn't in development. Are you on the right branch?")

    current_branch = c.run("git rev-parse --abbrev-ref HEAD").stdout.strip()
    c.run("git checkout master")
    releaser.update_changelog()
    c.run(f"git commit -am 'Prepare for {releaser.release_version} release'")
    c.run(f"git checkout {current_branch}")
    if current_branch != "master":
        commit = c.run("git rev-parse master").stdout.strip()
        c.run(f"invoke backport {commit}")

    releaser.update_version()
    if current_branch == "master":
        c.run(f"git commit -am 'Release {releaser.release_version}'")
    else:
        release_prefix = f"[{current_branch[len('release/') :]}]"
        c.run(f"git commit -am '{release_prefix} Release {releaser.release_version}'")
    c.run(
        f"git tag -am 'django-class-settings {releaser.release_version}' "
        f"{releaser.release_version}"
    )

    if publish:
        c.run("invoke publish")
    if bump:
        c.run(f"invoke bump {bump}")


@task
@check_git
def bump(c, version):
    allowed_versions = ["patch", "minor", "major"]
    if version not in allowed_versions:
        sys.exit(
            f"Version has to be one of {', '.join(allowed_versions)}, not {version!r}."
        )
    bumper = Bumper(c, version)
    if bumper.version.endswith("-dev"):
        sys.exit(
            "Current version is already in development. Are you on the right branch?"
        )

    current_branch = c.run("git rev-parse --abbrev-ref HEAD").stdout.strip()
    bumper.update_version()
    if current_branch == "master":
        c.run(f"git commit -am 'Bump version to {bumper.bump_version}'")
    else:
        bump_prefix = f"[{current_branch[len('release/') :]}]"
        c.run(f"git commit -am '{bump_prefix} Bump version to {bumper.bump_version}'")

    c.run("git checkout master")
    bumper.update_changelog()
    c.run(f"git commit -am 'Add stub for {bumper.release_version}'")
    c.run(f"git checkout {current_branch}")
    if current_branch != "master":
        commit = c.run("git rev-parse master").stdout.strip()
        c.run(f"invoke backport {commit}")


@task
@check_git
def publish(c):
    if get_version().endswith("-dev"):
        sys.exit("Current version is in development! Aborting.")

    c.run("poetry build")
    c.run("poetry publish")
