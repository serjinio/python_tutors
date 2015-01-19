
PROGS = cutting_sticks weights eratosthenes

.PHONY = all clean


all: $(PROGS)

cutting_sticks: cutting_sticks.c
	gcc -std=c99 -g -pthread -lpthread -o cutting_sticks cutting_sticks.c

weights: weights.c
	gcc -std=c99 -g -pthread -lpthread -o weights weights.c

eratosthenes: eratosthenes.c
	gcc -std=c99 -o eratosthenes eratosthenes.c -lm 

clean:
	rm $(PROGS)
