// CWE-78 exec() with request data (Node child_process)
const { exec } = require("child_process");
function run(req) {
    let cmd;
    cmd = "ping " + req.query["host"];
    exec(cmd);
}
