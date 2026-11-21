# CWE-502 safe variant: JSON instead of pickle
import json
from flask import request

def upload():
    return json.loads(request.data)
