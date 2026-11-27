// CWE-502 safe variant: JSON (Jackson)
import com.fasterxml.jackson.databind.ObjectMapper;

public class Store {
    public Object load(byte[] blob) throws Exception {
        return new ObjectMapper().readValue(blob, Object.class);
    }
}
