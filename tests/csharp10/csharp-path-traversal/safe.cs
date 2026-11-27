// CWE-22 safe variant: fixed base directory
public class FileController
{
    public void Get()
    {
        File.ReadAllText(Path.Combine("/srv/data", "report.txt"));
    }
}
