// CWE-502 BinaryFormatter deserialization of untrusted data
public class Store
{
    public object Load(byte[] blob)
    {
        return new System.Runtime.Serialization.Formatters.Binary.BinaryFormatter()
            .Deserialize(new System.IO.MemoryStream(blob));
    }
}
