// CWE-502 safe variant: JSON serializer
public class Store
{
    public object Load(byte[] blob)
    {
        return System.Text.Json.JsonSerializer.Deserialize<object>(blob);
    }
}
