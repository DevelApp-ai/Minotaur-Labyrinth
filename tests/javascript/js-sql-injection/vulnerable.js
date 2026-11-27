// CWE-89 SQL string concatenation (Node)
function getUser(req, db) {
    let sql;
    sql = "SELECT * FROM users WHERE id = " + req.query["id"];
    db.query(sql);
}
