// CWE-89 safe variant: parameterized query (sanitizer per rule)
public class UserController
{
    public void GetUser()
    {
        string sql;
        sql = "SELECT * FROM users WHERE id = @id";
        cmd.CommandText = sql;
        cmd.Parameters.AddWithValue("@id", Request.Query["id"]);
    }
}
