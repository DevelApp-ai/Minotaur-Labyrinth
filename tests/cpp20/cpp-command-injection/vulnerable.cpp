// CWE-78 OS command injection: system() with argv input.
// Sink per NIST/SAMATE Juliet C/C++ 1.3 CWE-78 (CC0 1.0); source adapted to argv per rule.
#include <cstdlib>

int main(int argc, char* argv[]) {
    char* cmd;
    cmd = argv[1];
    system(cmd);
    return 0;
}
