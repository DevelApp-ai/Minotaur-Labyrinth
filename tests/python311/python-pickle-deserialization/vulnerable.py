# CWE-502 insecure deserialization: pickle.loads on request data
import pickle
from flask import request

def upload():
    return pickle.loads(request.args["payload"])
