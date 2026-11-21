// CWE-89 safe variant: parameterized query
function getUser(req, db) {
    db.query("SELECT * FROM users WHERE id = ?", [req.query["id"]]);
}
