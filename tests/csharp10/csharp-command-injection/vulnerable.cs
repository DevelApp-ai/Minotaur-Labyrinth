// CWE-78 OS command injection: Process.Start with request data (OWASP Benchmark CWE-78 pattern, Apache-2.0)
public class RunController
{
    public void Run()
    {
        string args;
        args = Request.Query["cmd"];
        Process.Start("tool", args);
    }
}
