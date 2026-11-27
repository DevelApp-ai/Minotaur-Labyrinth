// Provenance: NIST/SAMATE Juliet Test Suite for Java 1.3 (CC0 1.0 Public Domain),
// file CWE328_Reversible_One_Way_Hash__MD5_01.java, good1() excerpt (SHA-512).
import java.security.MessageDigest;

public class WeakHash {
    public void good() throws Exception {
        MessageDigest messageDigest = MessageDigest.getInstance("SHA-512");
        byte[] hash = messageDigest.digest("password".getBytes());
    }
}
