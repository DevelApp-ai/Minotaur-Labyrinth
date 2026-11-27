// CWE-22 path traversal: File.ReadAllText with request data
public class FileController
{
    public void Get()
    {
        string path;
        path = Request.Query["file"];
        File.ReadAllText(path);
    }
}
