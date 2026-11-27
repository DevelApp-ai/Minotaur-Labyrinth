// CWE-78 OS command injection: sh -c with argv input
use std::process::Command;

fn main() {
    let cmd = std::env::args().nth(1).unwrap();
    Command::new("sh").arg("-c").arg(&cmd);
}
