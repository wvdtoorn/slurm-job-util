from setuptools import setup, find_packages

setup(
    name="slurm-job-util",
    version="0.1.0",
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
