import os
import subprocess
from typing import List

from .slurm_job import SlurmJob, SBatchCommand, RemoteHost
from .utils import logging


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


def watch_job(
    remote_host: str,
    job_id: int,
    watch_texts: List[str],
    wait_time: float = 0.01,
    timeout: float = 60,
) -> List[str]:
    host = RemoteHost(remote_host)
    return SlurmJob(job_id=job_id, host=host).watch_output_for_text(
        watch_texts, wait_time, timeout
    )


def cancel_job(remote_host: str, job_id: int) -> None:
    host = RemoteHost(remote_host)
    SlurmJob(job_id=job_id, host=host).cancel_slurm_job()


def my_queue(remote_host: str) -> str:
    host = RemoteHost(remote_host)
    return host.execute("squeue --me")
