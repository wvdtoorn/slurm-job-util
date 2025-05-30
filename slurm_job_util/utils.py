"""
Slurm Job Util

Copyright (c) 2024 by Wiep K. van der Toorn

"""

import logging
import os
import subprocess

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".slurm-job-util")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s", datefmt="%H:%M:%S", level=logging.INFO
)


def execute_on_host(host: str, command: str) -> subprocess.CompletedProcess:
    result = subprocess.run(["ssh", host, command], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(
            f"Failed to execute command on host! \nhost: {host}\ncommand: {command}\n{result.stderr}"
        )
    return result
