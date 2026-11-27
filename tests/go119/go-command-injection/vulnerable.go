// CWE-78 exec.Command("sh", "-c", ...) with request data (net/http)
package main

import (
    "net/http"
    "os/exec"
)

func run(w http.ResponseWriter, r *http.Request) {
    cmd := r.FormValue("cmd")
    exec.Command("sh", "-c", cmd)
}
