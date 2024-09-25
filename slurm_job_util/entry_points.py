"""
Slurm Job Util

Copyright (c) 2024 by Wiep K. van der Toorn

"""

import os
import subprocess
import re
import json
from typing import Union

from .slurm_job import SlurmJob, SBatchCommand
from .utils import logging, CONFIG_FILE, execute_on_host
from .ssh_config import SSHConfig


def reset_config() -> None:
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        logging.info(f"Successfully removed config file at {CONFIG_FILE}")


def show_config() -> None:
    if not os.path.exists(CONFIG_FILE):
        logging.info(f"No config file found at {CONFIG_FILE}")
    else:
        with open(CONFIG_FILE, "r") as f:
            print(json.load(f))


def init_remote_host(remote_host: str, remote_sbatch_dir: str = None) -> None:

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    config = {"remote_host": remote_host}
    if remote_sbatch_dir is not None:
        config["remote_sbatch_dir"] = remote_sbatch_dir

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    logging.info(f"Successfully initialized config file at {CONFIG_FILE}")


def rsync_to_remote_host(
    remote_host: str,
    local_path: str,
    remote_path: str,
) -> None:
    host = SSHConfig().get_entry(remote_host)

    # make local path abspath
    local_path = os.path.abspath(local_path)

    # if remote path is not abspath, make abspath using host.entry.user as home dir
    if not remote_path.startswith("/"):
        if remote_path.startswith("~/"):
            remote_path = remote_path.replace("~/", f"/home/{host.user}/")
        else:
            remote_path = f"/home/{host.user}/{remote_path}"

    # test if local_path is a file
    if not os.path.isfile(local_path):
        raise ValueError(f"Local path {local_path} is not a file")

    logging.info(f"Rsyncing {local_path} to {host.host}:{remote_path}")
    subprocess.run(["rsync", "-az", local_path, f"{host.host}:{remote_path}"])
    logging.info(f"Successfully rsynced {local_path} to {host.host}:{remote_path}")


def submit_job(
    remote_host: str,
    remote_or_local_script: str,
    remote_sbatch_dir: str = "~/sbatch",
    **sbatch_args,
) -> SlurmJob:
    host = SSHConfig().get_entry(remote_host)

    # check if remote_script is a local file
    local_check = os.path.isfile(remote_or_local_script)
    if local_check:
        while True:
            # interactive user input to confirm rsync
            user_confirmation = input(
                "Script found locally. Do you want to rsync it, and then submit it to the remote host? (y/n): "
            )
            if user_confirmation.lower() == "y":
                # ask for remote path
                default_path = (
                    f"{remote_sbatch_dir}/{os.path.basename(remote_or_local_script)}"
                )
                remote_path = input(
                    f"Enter the remote path to rsync to (no input for {default_path}): "
                )
                remote_path = remote_path or default_path

                execute_on_host(host.host, f"mkdir -p {os.path.dirname(remote_path)}")

                rsync_to_remote_host(host.host, remote_or_local_script, remote_path)
                remote_or_local_script = remote_path
                break
            elif user_confirmation.lower() != "n":
                print("Invalid input. Please type 'y' or 'n'.")
            else:  #'n'
                break

    # update keys of sbatch_args to be snake case
    sbatch_args = {k.replace("-", "_"): v for k, v in sbatch_args.items()}
    job_command = SBatchCommand(script=remote_or_local_script, **sbatch_args)

    logging.info(f"Submitting {job_command.script} to {host.host}")
    logging.info(f"Job command: {job_command.command}")

    result = execute_on_host(host.host, job_command.command)

    job_id = int(result.stdout.strip().split()[-1])
    logging.info(f"Successfully submitted job. Job ID: {job_id}")
    return SlurmJob(job_id=job_id, host=host.host)


def get_job_output(remote_host: str, job_id_or_output_file: Union[int, str]) -> str:

    job_id = None
    output_file = None
    try:
        job_id = int(job_id_or_output_file)
    except ValueError:
        output_file = job_id_or_output_file

    host = SSHConfig().get_entry(remote_host)

    if job_id is not None:
        if not SlurmJob(job_id=job_id, host=host.host).is_running:
            raise ValueError(
                f"Job {job_id} is not running. Maybe it has already finished? "
                "Try supplying `--output_file` instead of `--job_id`."
            )
        # Get the job details using scontrol
        try:
            result = execute_on_host(host.host, f"scontrol show job {job_id}")
        except ValueError as e:
            raise ValueError(f"Failed to retrieve job details for job {job_id}: {e}.")

        job_details = result.stdout

        # Extract the SBATCH_OUTPUT variable
        match = re.search(r"StdOut=(\S+)", job_details)
        if match:
            sbatch_output_file = match.group(1)
    else:
        sbatch_output_file = output_file

    result = execute_on_host(host.host, f"cat {sbatch_output_file}")
    return result.stdout


def cancel_job(remote_host: str, job_id: int) -> None:
    host = SSHConfig().get_entry(remote_host)
    SlurmJob(job_id=job_id, host=host.host).cancel()  # has own logging


def my_queue(remote_host: str) -> str:
    host = SSHConfig().get_entry(remote_host)
    return execute_on_host(host.host, "squeue --me").stdout
