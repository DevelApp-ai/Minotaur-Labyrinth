// CWE-95 safe variant: JSON.parse
function calc(req) {
    return JSON.parse(req.query["expr"]);
}
