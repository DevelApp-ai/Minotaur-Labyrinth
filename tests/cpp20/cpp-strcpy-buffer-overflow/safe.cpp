// CWE-120 safe variant: bounded copy
#include <cstring>

void copy_name(const char* src) {
    char dst[16];
    strncpy(dst, src, sizeof(dst));
}
