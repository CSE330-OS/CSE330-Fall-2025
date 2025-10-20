#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int swap_test_case(float scalar)
{
	int *array_constant;
	int mem_size = 268435456; //268435456*sizeof(int) = 1GB	

	mem_size 	= scalar * mem_size;
	array_constant 	= (int *) malloc (mem_size*sizeof(int));

	if (array_constant != NULL) 
	{
        for (int i=0; i<mem_size; i++) 
            array_constant[i] = i;

		while (1) {
			sleep(1);
		}
	}

	return 0;
}

int main(int argc, char *argv[])
{

	volatile float scalar;
	volatile int test_case = 1;

    if(argc == 2) {
        scalar = atof(argv[1]);
    }
    else {
        printf("Usage: ./testp5 <scalar>\n");
        exit(1);
    }

    swap_test_case(scalar);
	return 0;
}
