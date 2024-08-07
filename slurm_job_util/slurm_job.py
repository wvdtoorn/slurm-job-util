import subprocess
from typing import List
from dataclasses import dataclass, field

from .utils import logging, execute_on_host


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
    cpus_per_gpu: int = None
    mem_per_cpu: str = None
    mem: str = None
    qos: str = None
    export: List[str] = None  # ["VAR1=value", "VAR2=value"]
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
        _command = ["sbatch"]
        if self.time:
            _command.append(f"--time={self.time}")
        if self.cpus_per_task:
            _command.append(f"--cpus-per-task={self.cpus_per_task}")
        if self.cpus_per_gpu:
            _command.append(f"--cpus-per-gpu={self.cpus_per_gpu}")
        if self.mem_per_cpu:
            _command.append(f"--mem-per-cpu={self.mem_per_cpu}")
        if self.mem_per_gpu:
            _command.append(f"--mem-per-gpu={self.mem_per_gpu}")
        if self.mem:
            _command.append(f"--mem={self.mem}")
        if self.qos:
            _command.append(f"--qos={self.qos}")
        if self.partition:
            _command.append(f"--partition={self.partition}")
        if self.gpus:
            _command.append(f"--gres=gpu:{self.gpus}")
        if self.output:
            _command.append(f"--output={self.output}")
        if self.export:
            _command.append(f"--export={','.join(self.export)}")
        if self.nodes:
            _command.append(f"--nodes={self.nodes}")
        if self.ntasks:
            _command.append(f"--ntasks={self.ntasks}")
        if self.ntasks_per_node:
            _command.append(f"--ntasks-per-node={self.ntasks_per_node}")
        if self.array:
            _command.append(f"--array={self.array}")

        _command.append(self.script)
        _command = " ".join(_command)
        return _command


@dataclass
class SlurmJob:
    job_id: int
    host: str

    def execute_on_host(self, command: str) -> subprocess.CompletedProcess:
        return execute_on_host(self.host, command)

    def cancel(self) -> None:
        if self.status in ["PENDING", "RUNNING", "STOPPED"]:
            self.execute_on_host(f"scancel {self.job_id}")
            logging.info("Cancelled the SLURM job")

    @property
    def status(self) -> str:
        return self.execute_on_host(f"squeue -j {self.job_id} -h -o %T").stdout.strip()

    @property
    def is_running(self) -> bool:
        return self.status == "RUNNING"

    @property
    def has_completed(self) -> bool:
        return self.status == "COMPLETED"
