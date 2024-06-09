import os
import subprocess
import re
import json
from typing import Union

from .slurm_job import SlurmJob, SBatchCommand, RemoteHost
from .utils import logging, CONFIG_FILE


def init_remote_host(remote_host: str) -> None:

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump({"remote_host": remote_host}, f)


def rsync_to_remote_host(remote_host: str, local_path: str, remote_path: str) -> None:
    host = RemoteHost(remote_host)

    # make local path abs path
    local_path = os.path.abspath(local_path)

    # if remote path is not abspath, make abspath using host.entry.user as home dir
    if not remote_path.startswith("/"):
        remote_path = f"/home/{host.entry.user}/{remote_path}"

    # test if local_path is a file
    if not os.path.isfile(local_path):
        raise ValueError(f"Local path {local_path} is not a file")

    logging.info(f"Rsyncing {local_path} to {remote_path} on {remote_host}")
    subprocess.run(["rsync", "-az", local_path, f"{host.host}:{remote_path}"])
    logging.info(f"Successfully rsynced {local_path} to {host.host}:{remote_path}")


def submit_job(remote_host: str, remote_script: str, **kwargs) -> SlurmJob:
    job_command = SBatchCommand(script=remote_script, **kwargs)

    host = RemoteHost(remote_host)

    logging.info(f"Submitting {job_command.script} to {host.host}")
    logging.info(f"Job command: {job_command.command}")

    result = host.execute(job_command.command)

    if result.returncode != 0:
        raise ValueError(f"Failed to submit SLURM job: {result.stderr}")

    job_id = int(result.stdout.strip().split()[-1])
    logging.info(f"Successfully submitted job. Job ID: {job_id}")
    return SlurmJob(job_id=job_id, host=host)


def get_job_output(remote_host: str, job_id_or_output_file: Union[int, str]) -> str:

    job_id = None
    output_file = None
    try:
        job_id = int(job_id_or_output_file)
    except ValueError:
        output_file = job_id_or_output_file

    host = RemoteHost(remote_host)

    if job_id is not None:
        if not SlurmJob(job_id=job_id, host=host).is_running:
            raise ValueError(
                f"Job {job_id} is not running. Maybe it has already finished? "
                "Try supplying `--output_file` instead of `--job_id`."
            )
        # Get the job details using scontrol
        try:
            result = host.execute(f"scontrol show job {job_id}")
        except ValueError as e:
            raise ValueError(f"Failed to retrieve job details for job {job_id}: {e}.")

        job_details = result.stdout

        # Extract the SBATCH_OUTPUT variable
        match = re.search(r"StdOut=(\S+)", job_details)
        if match:
            sbatch_output_file = match.group(1)
    else:
        sbatch_output_file = output_file

    result = host.execute(f"cat {sbatch_output_file}")
    return result.stdout


def cancel_job(remote_host: str, job_id: int) -> None:
    host = RemoteHost(remote_host)
    SlurmJob(job_id=job_id, host=host).cancel_slurm_job()


def my_queue(remote_host: str) -> str:
    host = RemoteHost(remote_host)
    return host.execute("squeue --me")
