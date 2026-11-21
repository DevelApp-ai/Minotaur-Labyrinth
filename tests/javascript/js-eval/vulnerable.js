// CWE-95 eval() on request data
function calc(req) {
    return eval(req.query["expr"]);
}
