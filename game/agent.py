import subprocess

class Agent:
    def __init__(self, sid):
        self.sid = sid
        self.base_path = f"submissions/{self.sid}"
        with open(f"{self.base_path}/team.txt") as f:
            self.name = f.read().strip()
        self.process = subprocess.Popen(
            f"docker run -i -v ./{self.base_path}/:/submission/:ro bgc",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=True,
            universal_newlines=True,
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
