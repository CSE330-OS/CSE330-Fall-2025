#include <unistd.h>

int main() {
    /* Update 463 to match your syscall number as
     * per your implementation in kernel space */
    syscall(463);
    return 0;
}
