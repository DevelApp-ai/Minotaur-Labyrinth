// CWE-78 safe variant: execFile with argument list
const { execFile } = require("child_process");
function run(req) {
    execFile("ping", ["-c", "1", req.query["host"]]);
}
