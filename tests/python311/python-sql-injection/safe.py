# CWE-89 safe variant: parameterized query (sanitizer per rule)
from flask import request

def get_user(cursor):
    sql = "SELECT * FROM users WHERE id = %s"
    cursor.execute(sql, (request.args["id"],))
