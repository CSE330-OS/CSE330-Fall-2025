CC = gcc
CFLAGS = -std=c99

.PHONY: all
all: testp5

testp5: testp5.c
	$(CC) $(CFLAGS) $^ -o $@

.PHONY: clean
clean:
	-rm testp5
