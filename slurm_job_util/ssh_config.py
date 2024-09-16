import os
from dataclasses import dataclass


@dataclass
class SSHConfigEntry:
    host: str = None
    node: str = None
    port: str = None
    user: str = None
    proxy: str = None

    def __str__(self):
        return f"\n\nHost {self.host}\n\tHostName {self.node}\n\tPort {self.port}\n\tUser {self.user}\n\tProxyJump {self.proxy}\n\n"


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
                        entry.node = line.split(" ")[1].strip()
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

        with open(self.path, "w") as file:
            in_entry = False
            for line in lines:
                if line.strip() == f"Host {host}":
                    in_entry = True
                elif in_entry and line.strip().startswith("Host "):
                    in_entry = False
                if not in_entry:
                    file.write(line)

    def add_entry(self, entry: SSHConfigEntry) -> None:
        with open(self.path, "a") as file:
            file.write(str(entry))

    def update_config(self, entry: SSHConfigEntry) -> None:
        self.create_backup()
        if self.contains_host(entry.host):
            self.remove_entry(entry.host)
        self.add_entry(entry)
