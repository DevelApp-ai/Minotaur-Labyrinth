# CWE-95 safe variant: ast.literal_eval
import ast
from flask import request

def calc():
    return ast.literal_eval(request.args["expr"])
