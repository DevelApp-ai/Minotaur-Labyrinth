// CWE-79 XSS: req.query assigned to innerHTML (SecBench.js-style server-side JS)
function search(req, el) {
    let data = req.query["q"];
    let html;
    html = "<div>" + data + "</div>";
    el.innerHTML = html;
}
