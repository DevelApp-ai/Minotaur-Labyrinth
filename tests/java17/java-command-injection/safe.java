// CWE-78 safe variant: fixed program and arguments
public class RunServlet {
    public void run() throws Exception {
        new ProcessBuilder("tool", "--help").start();
    }
}
