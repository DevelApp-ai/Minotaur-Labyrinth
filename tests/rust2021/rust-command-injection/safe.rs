// CWE-78 safe variant: fixed program, no shell
use std::process::Command;

fn main() {
    Command::new("ls").arg("-l");
}
