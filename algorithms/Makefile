
PROGS = cutting_sticks weights eratosthenes cdecl samplehash

.PHONY = all clean


all: $(PROGS)

cutting_sticks: cutting_sticks.c
	gcc -std=c99 -g -pthread -lpthread -o cutting_sticks cutting_sticks.c

weights: weights.c
	gcc -std=c99 -g -pthread -lpthread -o weights weights.c

cdecl: cdecl.c
	gcc -std=c99 -g -Wall -o cdecl cdecl.c

eratosthenes: eratosthenes.c
	gcc -std=c99 -o eratosthenes eratosthenes.c -lm 

clean:
	rm $(PROGS)

cdecl_memtest: cdecl
	valgrind --leak-check=full ./cdecl

samplehash: samplehash.c
	gcc -std=c99 -o samplehash samplehash.c
