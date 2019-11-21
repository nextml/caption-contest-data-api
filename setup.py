import re, os, codecs
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    """
    https://packaging.python.org/guides/single-sourcing-package-version/
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("requirements.txt", "r") as f:
    packages = [x.strip("\n") for x in f.readlines()]

setup(
    name="caption_contest_data",
    version=find_version("caption_contest_data/__init__.py"),
    description="Data from The New Yorker Cartoon Caption Contest",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    keywords="data caption contest responses humor new-yorker",
    author="Scott Sievert",
    author_email="captions@stsievert.com",
    packages=["caption_contest_data"],
    install_requires=packages,
)
