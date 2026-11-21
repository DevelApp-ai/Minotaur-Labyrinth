// CWE-78 safe variant: fixed arguments, no user input
public class RunController
{
    public void Run()
    {
        Process.Start("tool", "--help");
    }
}
