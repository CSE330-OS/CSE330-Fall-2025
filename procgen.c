#include <sys/types.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>

void do_zombie()
{
    pid_t pid = fork();

    if (!pid) {
        sleep(1);
 	printf("%d\n", getpid());	
	fflush(stdout);
        exit(0);
    }

    else {
        while (1)
            sleep(100);
    }
}

void do_regular()
{
    while (1)
        sleep(100);
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        printf("./procgen <zombie|regular>\n");
        exit(1);
    }

    if (!strcmp(argv[1], "zombie"))
        do_zombie();

    else if (!strcmp(argv[1], "regular"))
        do_regular();

    else
        assert(0);
}

