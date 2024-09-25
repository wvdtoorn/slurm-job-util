"""
Slurm Job Util

Copyright (c) 2024 by Wiep K. van der Toorn

"""

from setuptools import setup, find_packages
import re

VERSIONFILE = "slurm_job_util/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name="slurm-job-util",
    version=verstr,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "slurm-job-util=slurm_job_util.main:main",
            "sju=slurm_job_util.main:main",
        ],
    },
    install_requires=[],
    author="Wiep van de Toorn",
    description="A utility for submitting and managing SLURM jobs locally",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wvdtoorn/slurm-job-util",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
