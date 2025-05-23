"""
Slurm Job Util

Copyright (c) 2024 by Wiep K. van der Toorn

"""

import argparse
import os
import json

from .utils import CONFIG_FILE
from .entry_points import (
    init_remote_host,
    show_config,
    reset_config,
    submit_job,
    rsync_to_remote_host,
    get_job_output,
    cancel_job,
    my_queue,
)


def read_config_file():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}


def main():
    config = read_config_file()
    default_remote_host = config.get("remote_host", None)
    default_remote_sbatch_dir = config.get("remote_sbatch_dir", None)

    parser = argparse.ArgumentParser(description="SLURM Job Utility")
    subparsers = parser.add_subparsers(
        dest="command", title="Subcommands", required=True
    )
    init_parser = subparsers.add_parser("init", help="Initialize remote host")
    init_parser.add_argument("remote_host", type=str, help="Remote host (HPC-login)")
    init_parser.add_argument(
        "--remote_sbatch_dir",
        type=str,
        default=None,
        help="Remote sbatch directory. Default location for local scripts to be copied to prior to submission.",
    )

    show_config_parser = subparsers.add_parser("show", help="Show config")

    reset_config_parser = subparsers.add_parser("reset", help="Reset config")

    # rsync_to_remote_host subparser
    rsync_parser = subparsers.add_parser("rsync", help="Rsync to remote host")
    rsync_parser.add_argument(
        "remote_host",
        type=str,
        nargs="?",
        default=default_remote_host,
        help="Remote host (HPC-login)",
    )
    rsync_parser.add_argument("local_path", type=str, help="Local path")
    rsync_parser.add_argument(
        "remote_path",
        type=str,
        help="Remote path, e.g. '/home/user/my_script.sbatch' or 'my_script.sbatch'",
    )

    # submit_job subparser
    submit_parser = subparsers.add_parser("submit", help="Submit SLURM job")
    submit_parser.add_argument(
        "remote_host",
        type=str,
        nargs="?",
        default=default_remote_host,
        help="Remote host",
    )
    submit_parser.add_argument(
        "remote_or_local_script",
        type=str,
        help="Sbatch script, can be a local file or a remote file",
    )
    submit_parser.add_argument(
        "--remote_sbatch_dir",
        type=str,
        default=default_remote_sbatch_dir,
        help="Remote sbatch directory. Default location for local scripts to be copied to prior to submission.",
    )
    submit_parser.add_argument(
        "--sbatch",
        nargs="*",
        help="Additional arguments for the job, e.g. --sbatch 'time=1:00:00' 'mem=1000M' "
        "'gres=gpu:1' 'mail-type=END,FAIL' 'mail-user=user@example.com'",
    )

    output_parser = subparsers.add_parser("output", help="Get SLURM job output")
    output_parser.add_argument(
        "remote_host",
        type=str,
        nargs="?",
        default=default_remote_host,
        help="Remote host (HPC-login)",
    )
    output_parser.add_argument(
        "job_id_or_output_file", type=str, help="Job ID or output file"
    )

    # cancel_job subparser
    cancel_parser = subparsers.add_parser("cancel", help="Cancel SLURM job")
    cancel_parser.add_argument(
        "remote_host",
        type=str,
        nargs="?",
        default=default_remote_host,
        help="Remote host (HPC-login)",
    )
    cancel_parser.add_argument("job_id", type=int, help="Job ID")

    # my_queue subparser
    queue_parser = subparsers.add_parser("queue", help="Show my SLURM queue")
    queue_parser.add_argument(
        "remote_host",
        type=str,
        nargs="?",
        default=default_remote_host,
        help="Remote host (HPC-login)",
    )

    args = parser.parse_args()

    def _check_remote_host(args):
        if args.remote_host is None:
            raise argparse.ArgumentError(
                args.remote_host,
                "Remote host is not set. Did you run 'sju init <remote_host>'?",
            )

    if args.command == "init":
        _check_remote_host(args)
        init_remote_host(args.remote_host, args.remote_sbatch_dir)
    elif args.command == "show":
        show_config()
    elif args.command == "reset":
        reset_config()
    elif args.command == "rsync":
        _check_remote_host(args)
        rsync_to_remote_host(args.remote_host, args.local_path, args.remote_path)
    elif args.command == "submit":
        _check_remote_host(args)

        sbatch_args = {}
        if args.sbatch:
            for arg in args.sbatch:
                key, value = arg.split("=", 1)
                if key == "export":
                    # Handle export argument specially
                    sbatch_args[key] = value.split(",")  # should be list
                else:
                    sbatch_args[key] = value

        submit_job(
            args.remote_host,
            args.remote_or_local_script,
            args.remote_sbatch_dir,
            **sbatch_args,
        )
    elif args.command == "output":
        _check_remote_host(args)
        print(get_job_output(args.remote_host, args.job_id_or_output_file))
    elif args.command == "cancel":
        _check_remote_host(args)
        cancel_job(args.remote_host, args.job_id)
    elif args.command == "queue":
        _check_remote_host(args)
        print(my_queue(args.remote_host))
    else:
        raise ValueError(f"Invalid command: {args.command}")


if __name__ == "__main__":
    main()
