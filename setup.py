from setuptools import setup

with open("requirements.txt", "r") as f:
    packages = [x.strip("\n") for x in f.readlines()]

setup(
    name="caption_contest_data",
    version="0.1-alpha",
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
    keywords="data caption contest humor",
    author="Scott Sievert",
    author_email="captions@stsievert.com",
    #  url="https://www.ettus.com/",
    #  license="GPLv3",
    #  package_dir={"": "caption_contest_data"},
    packages=["caption_contest_data"],
    install_requires=packages,
)
