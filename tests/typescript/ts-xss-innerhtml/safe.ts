// CWE-79 safe variant: textContent (sanitizer per rule)
function search(req: any, el: HTMLElement) {
    el.textContent = "<div>" + req.query["q"] + "</div>";
}
