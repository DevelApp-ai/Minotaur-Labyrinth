# CWE-95 exec() on request data
from flask import request

def run_code():
    exec(request.args["code"])
