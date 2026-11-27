// CWE-89 SQL injection (net/http + database/sql style)
package main

import (
    "database/sql"
    "net/http"
)

func getUser(r *http.Request, db *sql.DB) {
    data := r.URL.Query().Get("id")
    var query string
    query = "SELECT * FROM users WHERE id = " + data
    db.Query(query)
}
