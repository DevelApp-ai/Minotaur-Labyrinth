# CWE-95 safe variant: no exec; explicit dispatch table
from flask import request

HANDLERS = {"ping": lambda: "pong"}

def run_code():
    return HANDLERS[request.args["fn"]]()
