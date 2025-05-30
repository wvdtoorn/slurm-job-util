# SLURM Job Util

`slurm-job-util` is a utility package for managing SLURM jobs on remote hosts. It provides functionalities to rsync files, submit jobs, watch job outputs, cancel jobs, and view the job queue.

## Features

- Rsync files to and from remote hosts
- Submit SLURM jobs, using a local or remote sbatch script
- Watch SLURM job outputs
- Cancel SLURM jobs
- Show my SLURM queue

## Requirements

- `python` >=3.12 on local machine, no additional python packages required
- `rsync` on local machine
- remote host is a SLURM cluster
- valid entry in your `~/.ssh/config` file for the login node of the remote host

## Installation

To install the package, run:

```sh
pip install .
```

This will install the package and make the `slurm-job-util` and `sju` command available.
Both commands are equivalent.

## Usage

The `sju` command provides several subcommands for different functionalities:

### Initialize Config

```sh
sju init <remote_host>
```

Initialize the config file with the remote host's SSH config entry.
When this has been run, the `<remote_host>` argument can be omitted from subsequent commands.

### Show Config

```sh
sju show
```

Displays the current configuration.

### Reset Config

```sh
sju reset
```

Resets the config file to empty.

### Rsync to Remote Host

```sh
sju rsync <remote_host> <local_path> <remote_path>
# or, after init
sju rsync <local_path> <remote_path>
```

### Submit SLURM Job

```sh
sju submit <remote_host> <remote_or_local_script> [--kwargs key=value ...]
# or, after init
sju submit <remote_or_local_script> [--kwargs key=value ...]
```

Where `key=value` is a key-value pair of arguments to pass to the `sbatch` command.
If `<remote_or_local_script>` is a local file, you will be prompted to ask if you want to rsync it to the remote host prior to submitting the job.

For example, to submit a local sbatch script as a job with 4 CPUs per task and 1GB memory per CPU, you can use:

```sh
sju submit my-remote-host /path/to/local/script.sbatch --kwargs cpus-per-task=4 mem-per-cpu=1G
# or, after init
sju submit /path/to/local/script.sbatch --kwargs cpus-per-task=4 mem-per-cpu=1G
```

### Get SLURM Job Output

```sh
sju output <remote_host> <job_id>
# or, after init
sju output <job_id>
```

### Cancel SLURM Job

```sh
sju cancel <remote_host> <job_id>
# or, after init
sju cancel <job_id>
```

### Show My SLURM Queue

```sh
sju queue <remote_host>
# or, after init
sju queue
```

## Example

```sh
# Initialize the config file
sju init my.remote.host

# Rsync a file to a remote host
sju rsync /path/to/local/file /path/to/remote/file

# Submit a SLURM job
sju submit /path/to/remote/script.sh --kwargs arg1=value1 arg2=value2

# Watch a SLURM job
sju output 12345

# Cancel a SLURM job
sju cancel 12345

# Show my SLURM queue
sju queue
```

## License

This project is licensed under the MIT License.
