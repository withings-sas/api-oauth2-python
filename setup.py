"""
Custom setup.py to install the project as if it were a package. It parses
the requirements.txt to define its dependencies so it can remove itself as
the requirements are usually the output of `pip freeze`.
"""
import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
os.chdir(here)

about = {
    "__version__": "0.2.0"
}

with open(os.path.join(here, "requirements.txt")) as f:
    self = "withings_study_features==" + about["__version__"] + "\n"
    self_git_pattern = re.compile(
        r"^-e git\+git@git.*#egg=withings_api_example"
    )

    requirements = [
        line.strip()
        for line in f
        if line != self and not re.match(self_git_pattern, line)
    ]


setup(
    name="withings_study_features",
    version=about["__version__"],
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    install_requires=requirements,
)
