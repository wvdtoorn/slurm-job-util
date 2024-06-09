import argparse

from .entry_points import (
    submit_job,
    rsync_to_remote_host,
    watch_job,
    cancel_job,
    my_queue,
)


def main():
    parser = argparse.ArgumentParser(description="SLURM Job Utility")
    subparsers = parser.add_subparsers(
        dest="command", title="Subcommands", required=True
    )

    # rsync_to_remote_host subparser
    rsync_parser = subparsers.add_parser("rsync", help="Rsync to remote host")
    rsync_parser.add_argument("remote_host", type=str, help="Remote host (HPC-login)")
    rsync_parser.add_argument("local_path", type=str, help="Local path")
    rsync_parser.add_argument(
        "remote_path",
        type=str,
        help="Remote path, e.g. '/home/user/my_script.sbatch' or 'my_script.sbatch'",
    )

    # submit_job subparser
    submit_parser = subparsers.add_parser("submit", help="Submit SLURM job")
    submit_parser.add_argument("remote_host", type=str, help="Remote host")
    submit_parser.add_argument("remote_script", type=str, help="Remote script")
    submit_parser.add_argument(
        "--sbatch",
        nargs="*",
        help="Additional arguments for the job, e.g. --sbatch 'time=1:00:00' 'mem=1000M' "
        "'gres=gpu:1' 'mail-type=END,FAIL' 'mail-user=user@example.com'",
    )

    # watch_job subparser
    watch_parser = subparsers.add_parser(
        "watch", help="Watch SLURM job output for text"
    )
    watch_parser.add_argument("remote_host", type=str, help="Remote host (HPC-login)")
    watch_parser.add_argument("job_id", type=int, help="Job ID")
    watch_parser.add_argument("watch_texts", nargs="+", help="Texts to watch for")
    watch_parser.add_argument(
        "--wait_time", type=float, default=0.01, help="Check interval"
    )
    watch_parser.add_argument("--timeout", type=float, default=60, help="Timeout")

    # cancel_job subparser
    cancel_parser = subparsers.add_parser("cancel", help="Cancel SLURM job")
    cancel_parser.add_argument("remote_host", type=str, help="Remote host (HPC-login)")
    cancel_parser.add_argument("job_id", type=int, help="Job ID")

    # my_queue subparser
    queue_parser = subparsers.add_parser("queue", help="Show my SLURM queue")
    queue_parser.add_argument("remote_host", type=str, help="Remote host (HPC-login)")

    args = parser.parse_args()

    if args.command == "rsync":
        rsync_to_remote_host(args.remote_host, args.local_path, args.remote_path)
    elif args.command == "submit":
        submit_job(
            args.remote_host,
            args.remote_script,
            **dict(arg.split("=") for arg in args.kwargs)
        )
    elif args.command == "watch":
        watch_job(
            args.remote_host,
            args.job_id,
            args.watch_texts,
            args.wait_time,
            args.timeout,
        )
    elif args.command == "cancel":
        cancel_job(args.remote_host, args.job_id)
    elif args.command == "queue":
        print(my_queue(args.remote_host))


if __name__ == "__main__":
    main()
