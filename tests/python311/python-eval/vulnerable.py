# CWE-95 eval() on request data
from flask import request

def calc():
    return eval(request.args["expr"])
