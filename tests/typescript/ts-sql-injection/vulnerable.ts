// CWE-89 SQL injection (Express + node-postgres style)
function getUser(req: any, db: any) {
    const data = req.query["id"];
    let sql: string;
    sql = "SELECT * FROM users WHERE id = " + data;
    db.query(sql);
}
