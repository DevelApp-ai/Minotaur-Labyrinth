// CWE-95 safe variant: JSON.parse
function calc(req: any) {
    return JSON.parse(req.query["expr"]);
}
