// CWE-327 safe variant: SHA-256
using System.Security.Cryptography;

public class HashUtil
{
    public byte[] Hash(string input)
    {
        return SHA256.Create().ComputeHash(System.Text.Encoding.UTF8.GetBytes(input));
    }
}
