// CWE-89 SQL injection, OWASP Benchmark CWE-89 servlet pattern (Apache-2.0)
import java.sql.Statement;
import javax.servlet.http.HttpServletRequest;

public class UserServlet {
    public void doGet(HttpServletRequest request, Statement statement) throws Exception {
        String data = request.getParameter("id");
        String sql;
        sql = "SELECT * FROM users WHERE id = " + data;
        statement.executeQuery(sql);
    }
}
