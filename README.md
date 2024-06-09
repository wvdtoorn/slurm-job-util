# SLURM Job Util

`slurm-job-util` is a utility package for managing SLURM jobs on remote hosts. It provides functionalities to rsync files, submit jobs, watch job outputs, cancel jobs, and view the job queue.

## Installation

To install the package, run:

```sh
pip install .
```

This will install the package and make the `sju` command available.

## Usage

The `sju` command provides several subcommands for different functionalities:

### Rsync to Remote Host

```sh
sju rsync <remote_host> <local_path> <remote_path>
```

### Submit SLURM Job

```sh
sju submit <remote_host> <remote_script> [--kwargs key=value ...]
```

Where `key=value` is a key-value pair of arguments to pass to the `sbatch` command.
For example, to submit the job with 4 CPUs per task and 1GB memory per CPU, you can use:

```sh
sju submit my-remote-host /path/to/remote/script.sbatch --kwargs cpus-per-task=4 mem-per-cpu=1G
```

### Watch SLURM Job

```sh
sju watch <remote_host> <job_id> <watch_texts> [--wait_time <wait_time>] [--timeout <timeout>]
```

Watch the job output for specific text. If the text is not found within the timeout, the command will exit with a non-zero exit code. If the text is found, the whole line containing the text will be printed to stdout.

### Cancel SLURM Job

```sh
sju cancel <remote_host> <job_id>
```

### Show My SLURM Queue

```sh
sju queue <remote_host>
```

## Example

```sh
# Rsync a file to a remote host
sju rsync my.remote.host /path/to/local/file /path/to/remote/file

# Submit a SLURM job
sju submit my.remote.host /path/to/remote/script.sh --kwargs arg1=value1 arg2=value2

# Watch a SLURM job
sju watch my.remote.host 12345 "Some text" "Some other text" --wait_time 0.1 --timeout 120

# Cancel a SLURM job
sju cancel my.remote.host 12345

# Show my SLURM queue
sju queue my.remote.host
```

## License

This project is licensed under the MIT License.
