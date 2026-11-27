// CWE-95 eval() on request data
function calc(req: any) {
    return eval(req.query["expr"]);
}
