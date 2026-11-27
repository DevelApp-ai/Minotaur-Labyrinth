// CWE-89 safe variant: parameterized query (sanitizer per rule)
package main

import (
    "database/sql"
    "net/http"
)

func getUser(r *http.Request, db *sql.DB) {
    db.Query("SELECT * FROM users WHERE id = $1", r.URL.Query().Get("id"))
}
