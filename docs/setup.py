# TODO: Switch to pyproject.toml once pip implements PEP 517
from setuptools import find_packages, setup

setup(
    name="docs",
    packages=find_packages(),
    install_requires=["mkdocs~=1.0", "markdown<3", "py-gfm", "lxml"],
    entry_points={
        "mkdocs.plugins": ["index_generator = plugins.generators:IndexGeneratorPlugin"]
    },
)
