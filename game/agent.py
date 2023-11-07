import subprocess
import signal
import resource

MB = 1024*1024
TIMEOUT = 10
COMPILE_TIMEOUT = 30
MEMLIMIT = 50*MB


class Agent:
    def __init__(self, sid):
        self.sid = sid
        self.base_path = f"/submissions/{self.sid}"
        self.entrypoint = self.read_team_file("entrypoint.txt")
        self.name = self.read_team_file("team.txt")
        assert self.compile()
        def set_limits():
            resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT, TIMEOUT))
            resource.setrlimit(resource.RLIMIT_DATA, (MEMLIMIT, MEMLIMIT))
        self.process = subprocess.Popen(
            f"{self.base_path}/run {self.base_path}/{self.entrypoint}",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=True,
            universal_newlines=True,
            preexec_fn=set_limits,
        )

    def read_team_file(self, filename):
        with open(f"{self.base_path}/{filename}") as f:
            return f.read().strip()

    def compile(self):
        return (
            subprocess.run(
                f"{self.base_path}/compile {self.base_path}/{self.entrypoint}",
                shell=True,
                timeout=COMPILE_TIMEOUT,
            ).returncode
            == 0
        )

    def kill(self):
        self.process.kill()

    def is_alive(self):
        return self.process.poll() is None

    def read(self):
        assert self.is_alive()
        return self.process.stdout.readline()

    def write(self, data):
        assert self.is_alive()
        self.process.stdin.write(f"{data}\n")
        self.process.stdin.flush()
