import subprocess
import signal


class Agent:
    def __init__(self, sid):
        self.sid = sid
        self.base_path = f"/submissions/{self.sid}"
        self.entrypoint = self.read_team_file("entrypoint.txt")
        self.name = self.read_team_file("team.txt")
        assert self.compile()
        self.process = subprocess.Popen(
            f"timeout 10 {self.base_path}/run {self.base_path}/{self.entrypoint}",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
        )

    def read_team_file(self, filename):
        with open(f"{self.base_path}/{filename}") as f:
            return f.read().strip()

    def compile(self):
        return (
            subprocess.run(
                f"sh {self.base_path}/compile {self.base_path}/{self.entrypoint}",
                shell=True,
                timeout=10,
            ).returncode
            == 0
        )

    def pause(self):
        self.process.send_signal(signal.SIGSTOP)

    def resume(self):
        self.process.send_signal(signal.SIGCONT)

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
