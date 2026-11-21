// Provenance: NIST/SAMATE Juliet Test Suite for Java 1.3 (CC0 1.0 Public Domain),
// file CWE328_Reversible_One_Way_Hash__MD5_01.java, bad() excerpt. CWE-328.
import java.security.MessageDigest;

public class WeakHash {
    public void bad() throws Exception {
        MessageDigest messageDigest = MessageDigest.getInstance("MD5");
        byte[] hash = messageDigest.digest("password".getBytes());
    }
}
