import os
import subprocess
import time

from typing import List, Union
from dataclasses import dataclass, field

from .ssh_config import SSHConfig, SSHConfigEntry
from .utils import logging


@dataclass
class RemoteHost:
    host: str

    ssh_config_path: str = os.path.expanduser("~/.ssh/config")

    entry: SSHConfigEntry = None

    def __post_init__(self):
        if not self.host:
            raise ValueError("Host is required")

        ssh_config = SSHConfig(self.ssh_config_path)
        self.entry = ssh_config.get_entry(self.host)  # raises if not found

    def execute(
        self, command: str, stdout: bool = False
    ) -> Union[str, subprocess.CompletedProcess]:
        result = subprocess.run(
            ["ssh", self.host, command], capture_output=True, text=True, check=True
        )
        if stdout:
            return result.stdout
        return result


@dataclass
class SBatchCommand:
    """
    A class to represent a SLURM sbatch command.

    This class does not check the validity of the command.
    It is the responsibility of the user to provide a valid parameter configuration.
    """

    script: str
    time: str = None
    cpus_per_task: int = None
    mem_per_cpu: str = None
    mem: str = None
    qos: str = None
    export: List[str] = field(default_factory=[])  # ["VAR1=value", "VAR2=value"]
    partition: str = None
    gpus: int = None
    mem_per_gpu: int = None
    nodes: int = None
    ntasks: int = None
    ntasks_per_node: int = None
    array: str = None
    output: str = None

    @property
    def command(self) -> str:
        command = ["sbatch"]
        if self.time:
            command.append(f"--time={self.time}")
        if self.cpus_per_task:
            command.append(f"--cpus-per-task={self.cpus_per_task}")
        if self.mem_per_cpu:
            command.append(f"--mem-per-cpu={self.mem_per_cpu}")
        if self.mem:
            command.append(f"--mem={self.mem}")
        if self.qos:
            command.append(f"--qos={self.qos}")
        if self.partition:
            command.append(f"--partition={self.partition}")
        if self.output:
            command.append(f"--output={self.output}")
        if self.export:
            command.append(f"--export={','.join(self.export)}")
        if self.nodes:
            command.append(f"--nodes={self.nodes}")
        if self.ntasks:
            command.append(f"--ntasks={self.ntasks}")
        if self.ntasks_per_node:
            command.append(f"--ntasks-per-node={self.ntasks_per_node}")
        if self.array:
            command.append(f"--array={self.array}")

        command.append(self.script)
        command = " ".join(command)
        return command


@dataclass
class SlurmJob:
    job_id: int
    host: RemoteHost

    def cancel_slurm_job(self) -> None:
        if self.job_status in ["PENDING", "RUNNING", "STOPPED"]:
            subprocess.run(["ssh", self.host.host, f"scancel {self.job_id}"])
            logging.info("Cancelled the SLURM job")

    @property
    def job_status(self) -> str:
        result = subprocess.run(
            [
                "ssh",
                self.host.host,
                f"squeue -j {self.job_id} -h -o %T",
            ],
            capture_output=True,
            text=True,
        )
        job_status = result.stdout.strip()
        return job_status

    @property
    def is_running(self) -> bool:
        return self.job_status == "RUNNING"

    @property
    def has_completed(self) -> bool:
        return self.job_status == "COMPLETED"
