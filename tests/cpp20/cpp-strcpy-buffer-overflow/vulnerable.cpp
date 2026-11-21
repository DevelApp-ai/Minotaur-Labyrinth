// CWE-120 buffer copy without bounds check (strcpy); Juliet C/C++ 1.3 CWE-121 family (CC0 1.0)
#include <cstring>

void copy_name(const char* src) {
    char dst[16];
    strcpy(dst, src);
}
