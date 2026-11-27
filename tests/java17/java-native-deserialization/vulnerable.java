// CWE-502 native deserialization (ObjectInputStream.readObject)
import java.io.ObjectInputStream;
import java.io.ByteArrayInputStream;

public class Store {
    public Object load(byte[] blob) throws Exception {
        return new ObjectInputStream(new ByteArrayInputStream(blob)).readObject();
    }
}
