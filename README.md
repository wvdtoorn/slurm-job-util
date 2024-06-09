# SLURM Job Util

`slurm-job-util` is a utility package for managing SLURM jobs on remote hosts. It provides functionalities to rsync files, submit jobs, watch job outputs, cancel jobs, and view the job queue.

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
sju submit <remote_host> <remote_script> [--kwargs key=value ...]
# or, after init
sju submit <remote_script> [--kwargs key=value ...]
```

Where `key=value` is a key-value pair of arguments to pass to the `sbatch` command.
For example, to submit the job with 4 CPUs per task and 1GB memory per CPU, you can use:

```sh
sju submit my-remote-host /path/to/remote/script.sbatch --kwargs cpus-per-task=4 mem-per-cpu=1G
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
