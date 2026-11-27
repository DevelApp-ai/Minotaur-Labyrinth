// CWE-89 safe variant: bound parameter (sqlite3_prepare_v2 + bind)
#include <sqlite3.h>

int main() {
    sqlite3_stmt* stmt = nullptr;
    sqlite3_prepare_v2(NULL, "SELECT * FROM users WHERE id = ?", -1, &stmt, NULL);
    return 0;
}
