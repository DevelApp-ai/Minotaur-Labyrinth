// CWE-327 weak hash: MD5 (cf. NIST/SAMATE Juliet Java 1.3 CWE-328 MD5 case, CC0 1.0)
using System.Security.Cryptography;

public class HashUtil
{
    public byte[] Hash(string input)
    {
        return MD5.Create().ComputeHash(System.Text.Encoding.UTF8.GetBytes(input));
    }
}
