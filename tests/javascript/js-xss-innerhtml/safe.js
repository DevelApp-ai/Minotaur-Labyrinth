// CWE-79 safe variant: textContent (sanitizer per rule)
function search(req, el) {
    el.textContent = "<div>" + req.query["q"] + "</div>";
}
