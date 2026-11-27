// CWE-89 safe variant: parameterized query
function getUser(req: any, db: any) {
    db.query("SELECT * FROM users WHERE id = $1", [req.query["id"]]);
}
