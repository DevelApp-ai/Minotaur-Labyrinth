// CWE-79 innerHTML with request data (Express)
function search(req: any, el: HTMLElement) {
    const data = req.query["q"];
    let html: string;
    html = "<div>" + data + "</div>";
    el.innerHTML = html;
}
