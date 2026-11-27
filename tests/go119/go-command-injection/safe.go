// CWE-78 safe variant: fixed program, no shell
package main

import "os/exec"

func run() {
    exec.Command("tool", "--help")
}
