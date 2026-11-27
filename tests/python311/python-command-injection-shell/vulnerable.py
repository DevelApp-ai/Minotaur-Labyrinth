# CWE-78 shell=True with request data (Flask)
import subprocess
from flask import request

def run():
    cmd = "ping " + request.args["host"]
    subprocess.run(cmd, shell=True)
