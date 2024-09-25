"""
Slurm Job Util

Copyright (c) 2024 by Wiep K. van der Toorn

"""

import os
from dataclasses import dataclass


@dataclass
class SSHConfigEntry:
    host: str
    hostname: str | None = None
    port: str | None = None
    user: str | None = None
    proxy: str | None = None

    @property
    def hostname_str(self) -> str:
        if self.hostname is None:
            return ""
        return f"\n\tHostName {self.hostname}"

    @property
    def port_str(self) -> str:
        if self.port is None:
            return ""
        return f"\n\tPort {self.port}"

    @property
    def user_str(self) -> str:
        if self.user is None:
            return ""
        return f"\n\tUser {self.user}"

    @property
    def proxy_str(self) -> str:
        if self.proxy is None:
            return ""
        return f"\n\tProxyJump {self.proxy}"

    def __str__(self):
        return f"\n\nHost {self.host}{self.hostname_str}{self.port_str}{self.user_str}{self.proxy_str}\n\n"


class SSHConfig:
    path: str = os.path.expanduser("~/.ssh/config")

    def __init__(self, path=None):
        if path is not None:
            self.path = path
        self.exists()

    def exists(self):
        if not os.path.exists(self.path):
            raise ValueError(f"SSH config file {self.path} does not exist")
        return True

    def create_backup(self):
        backup_ssh_config_path = self.path + ".bak"
        os.system(f"cp {self.path} {backup_ssh_config_path}")

    def contains_host(self, host: str) -> bool:
        return any(line.strip() == f"Host {host}" for line in open(self.path))

    def get_entry(self, host: str) -> SSHConfigEntry:
        # read ssh config file until the entry Host host begins, read it until the next entry or the end of the file (whichever comes first) and remove empty lines
        if not self.contains_host(host):
            raise ValueError(f"Remote host '{host}' not found in {self.path}")

        entry = SSHConfigEntry(host=host)
        in_entry = False
        with open(self.path, "r") as file:
            for line in file:
                line = line.strip()  # remove leading/trailing whitespace
                if line == f"Host {host}":
                    in_entry = True
                elif in_entry:
                    if line.startswith("Host "):  # trailing space to not match HostName
                        break  # new entry
                    elif line.strip() == "":
                        break  # new entry
                    elif line.startswith("HostName"):
                        entry.hostname = line.split(" ")[1].strip()
                    elif line.startswith("Port"):
                        entry.port = line.split(" ")[1].strip()
                    elif line.startswith("User"):
                        entry.user = line.split(" ")[1].strip()
                    elif line.startswith("ProxyJump"):
                        entry.proxy = line.split(" ")[1].strip()
        return entry

    def remove_entry(self, host: str) -> None:
        with open(self.path, "r") as file:
            lines = file.readlines()

        new_lines = []

        in_entry = False
        for line in lines:
            if line.strip() == f"Host {host}":
                in_entry = True
            elif in_entry and line.startswith("Host "):
                in_entry = False
            if not in_entry:
                new_lines.append(line)

        # remove trailing empty lines
        while new_lines and new_lines[-1].strip() == "":
            new_lines.pop()

        with open(self.path, "w") as file:
            file.writelines(new_lines)

    def add_entry(self, entry: SSHConfigEntry) -> None:

        with open(self.path, "a") as file:
            file.write("\n")
            file.write(str(entry))

    def update_config(self, entry: SSHConfigEntry) -> None:
        self.create_backup()

        assert entry.host is not None, "Host is required in SSHConfigEntry"
        if self.contains_host(entry.host):
            self.remove_entry(entry.host)
        self.add_entry(entry)
