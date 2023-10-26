import subprocess
from dataclasses import dataclass


@dataclass
class Language:
    extension: str
    compiler: str
    runner: str


SCRIPTS = './scripts'
PYTHON = Language('py', None, f'{SCRIPTS}/pypy')
JAVASCRIPT = Language('js', None, f'{SCRIPTS}/bun')
CPP = Language('cpp', f'{SCRIPTS}/gpp', f'{SCRIPTS}/run')
available_languages = [PYTHON, JAVASCRIPT, CPP]


class Agent:
    def __init__(self, path):
        self.path = path
        self.lang = next(filter(
            lambda l: l.extension == path.split('.')[-1],
            available_languages
        ))
        self._is_alive = self.compile()
        self.process = subprocess.Popen(
            f'{self.lang.runner} {self.path}',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
        )
        assert self.is_alive()

    def compile(self):
        if self.lang.compiler is None:
            return True
        return subprocess.call([self.lang.compiler, self.path]) == 0
    
    def is_alive(self):
        self._is_alive = self._is_alive and self.process.poll() is None
        return self._is_alive

    def read(self):
        assert self.is_alive()
        return self.process.stdout.readline()
    
    def write(self, data):
        assert self.is_alive()
        self.process.stdin.write(f'{data}\n')
        self.process.stdin.flush()
