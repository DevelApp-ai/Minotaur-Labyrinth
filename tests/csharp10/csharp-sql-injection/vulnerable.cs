// CWE-89 SQL injection, modeled on OWASP Benchmark CWE-89 servlet pattern (Apache-2.0)
public class UserController
{
    public void GetUser()
    {
        string data;
        data = Request.Query["id"];
        string sql;
        sql = "SELECT * FROM users WHERE id = " + data;
        cmd.CommandText = sql;
        cmd.ExecuteNonQuery();
    }
}
