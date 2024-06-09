import os
import subprocess
import time

from typing import List
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

    def execute(self, command: str) -> str:
        result = subprocess.run(
            ["ssh", self.host, command],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ConnectionError(
                f"Execution of command {command} on {self.host} failed: {result.stderr}"
            )
        return result.stdout


@dataclass
class SBatchCommand:
    """
    A class to represent a SLURM sbatch command.

    This class does not check the validity of the command.
    It is the responsibility of the user to provide a valid parameter configuration.
    """

    script: str = "script.sbatch"
    time: str = "3:00:00"
    cpus_per_task: int = 8
    mem_per_cpu: str = "1G"
    mem: str = "16G"
    qos: str = "hiprio"
    output: str = None
    export: List[str] = field(default_factory=[])  # ["VAR1=value", "VAR2=value"]
    partition: str = None
    gpus: int = None
    mem_per_gpu: int = None
    nodes: int = None
    ntasks: int = None
    ntasks_per_node: int = None
    array: str = None

    def __post_init__(self):
        # find extension
        extension = os.path.splitext(self.script)[1]

        # check if ext is empty
        has_ext = extension != ""
        if has_ext:
            self.output = self.script.replace(f"{extension}", ".out")
        else:
            self.output = self.script + ".out"

    @property
    def output(self) -> str:
        return self.script.replace(".sbatch", ".out")

    @property
    def command(self) -> str:
        command = ["sbatch"]
        if self.time:
            command.append(f"--time={self.time}")
        if self.cpus:
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
    def job_running(self) -> bool:
        return self.job_status == "RUNNING"

    @property
    def job_completed(self) -> bool:
        return self.job_status == "COMPLETED"

    def watch_output_for_text(
        self, watch_texts: List[str], wait_time: float = 0.01, timeout: float = 60
    ) -> List[str]:
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ["ssh", self.host.host, f"cat {self.job_command.output}"],
                capture_output=True,
                text=True,
            )
            output = result.stdout
            found_texts = []
            for line in output.splitlines():
                for watch_text in watch_texts:
                    if watch_text in line:
                        found_texts.append(line)
                if len(found_texts) == len(watch_texts):
                    return found_texts
            time.sleep(wait_time)
        raise TimeoutError(f"Timed out waiting for {watch_texts}")
