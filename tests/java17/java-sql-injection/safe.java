// CWE-89 safe variant: PreparedStatement parameter (sanitizer per rule)
import javax.servlet.http.HttpServletRequest;

public class UserServlet {
    public void doGet(HttpServletRequest request, java.sql.PreparedStatement preparedStatement) throws Exception {
        preparedStatement.setString(1, request.getParameter("id"));
        preparedStatement.executeQuery();
    }
}
