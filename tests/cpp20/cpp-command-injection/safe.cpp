// CWE-78 safe variant: fixed command, no user input
#include <cstdlib>

int main() {
    system("ls -l");
    return 0;
}
