// CWE-89 SQL statement built from argv, executed via sqlite3_exec (Juliet CWE-89 sink shape, CC0 1.0)
#include <sqlite3.h>
#include <string>

int main(int argc, char* argv[]) {
    std::string sql;
    sql = "SELECT * FROM users WHERE id = ";
    sql += argv[1];
    sqlite3_exec(NULL, sql.c_str(), NULL, NULL, NULL);
    return 0;
}
