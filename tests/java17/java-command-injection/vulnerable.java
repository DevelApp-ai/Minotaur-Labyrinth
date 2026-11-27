// CWE-78 Runtime.exec with request parameter (OWASP Benchmark CWE-78 servlet pattern, Apache-2.0)
import javax.servlet.http.HttpServletRequest;

public class RunServlet {
    public void doGet(HttpServletRequest request) throws Exception {
        String cmd = request.getParameter("cmd");
        Runtime.getRuntime().exec(cmd);
    }
}
