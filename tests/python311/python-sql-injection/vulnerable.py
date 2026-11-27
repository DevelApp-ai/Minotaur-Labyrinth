# CWE-89 SQL injection (Flask style), modeled on OWASP Benchmark CWE-89 pattern
from flask import request

def get_user(cursor):
    data = request.args["id"]
    sql = "SELECT * FROM users WHERE id = " + data
    cursor.execute(sql)
