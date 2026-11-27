# CWE-78 safe variant: no shell, argument list
import subprocess
from flask import request

def run():
    subprocess.run(["ping", "-c", "1", request.args["host"]])
