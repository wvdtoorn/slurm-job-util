import logging
import os


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".slurm-job-util")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s", datefmt="%H:%M:%S", level=logging.INFO
)
