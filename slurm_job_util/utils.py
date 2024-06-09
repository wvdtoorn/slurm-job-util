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
    return subprocess.run(
        ["ssh", host, command], check=True, capture_output=True, text=True
    )
