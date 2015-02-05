
#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <stdbool.h>


typedef struct Pair {
  int weight;
  int strength;
} Pair;

typedef struct IntTable {
  int *data;
  int nrows;
  int ncolumns;
} IntTable;

void int_table_fill(IntTable *tbl, int value) {
  for (int i = 0; i < tbl->nrows * tbl->ncolumns; i++) {
    *(tbl->data + i) = value;
  }  
}

IntTable *int_table_new(int rows, int columns) {
  IntTable *tbl = malloc(sizeof(IntTable));
  int *data = malloc(sizeof(int) * rows * columns);
  if (tbl == NULL || data == NULL) {
    return NULL;
  }
  
  tbl->data = data;
  tbl->nrows = rows;
  tbl->ncolumns = columns;
  int_table_fill(tbl, 0);
  
  return tbl;
}

void int_table_free(IntTable *tbl) {
  free(tbl->data);
  return free(tbl);
}

int *int_table_row(IntTable *tbl, int row) {
  if (row >= 0 && row < tbl->nrows) {
    return tbl->data + (tbl->ncolumns * row);
  } else {
    return NULL;
  }
}

int int_table_get(IntTable *tbl, int row, int column) {
  int *rowptr = int_table_row(tbl, row);
  return *(rowptr + column);
}     

void int_table_set(IntTable *tbl, int row, int column, int value) {
  *(int_table_row(tbl, row) + column) = value;
}

void int_table_print(IntTable *tbl) {
  for (int i = 0; i < tbl->nrows; i++) {
    for (int k = 0; k < tbl->ncolumns; k++) {
      printf("%5i", int_table_get(tbl, i, k));
    }
    printf("\n");    
  }
}

static void fill(int *data, int length, int value) {
  for (int *p = data; p != data + length; p += 1) {
    *p = value;
  }
}

static int int_cmp_rev(const void *a, const void *b) { 
  const int *ia = (const int *)a; // casting pointer types 
  const int *ib = (const int *)b;
  return *ib  - *ia; 
} 

static int find_by_value(int arr[], int length, int value) {
  for (int i = 0; i < length; i++) {
    if (arr[i] == value) return i;
  }

  return -1;
}

static bool is_already_used_item(int item_idx, int seq_length, IntTable *parents) {
  int idx = item_idx;

  while ((idx = int_table_get(parents, seq_length, idx)) != -1) {
    if (item_idx == idx) {
      //printf("element with index %i already used in parent sequence\n", idx);
      return true;
    }
    seq_length -= 1;
  }

  // printf("element with index %i is not used in parent sequence\n", item_idx);
  return false;
}

int find_parent(int seq_length, int child_idx, IntTable *capacities,
		IntTable *parents) {
  /* printf("searching for suitable parent element for sequence length: %i\n", */
  /* 	 seq_length); */
  int caps_sorted[capacities->ncolumns];
  memcpy(caps_sorted, int_table_row(capacities, seq_length - 1),
	 capacities->ncolumns * sizeof(int));
  qsort(caps_sorted, capacities->ncolumns, sizeof(int), int_cmp_rev);

  for (int i = 0; i < capacities->ncolumns; i++) {
    int parent_idx = find_by_value(int_table_row(capacities, seq_length - 1),
				   capacities->ncolumns, caps_sorted[i]);
    /* printf("checking element with index: %i and capacity: %i\n", */
    /* 	   parent_idx, caps_sorted[i]); */
    if (parent_idx == child_idx) {
      continue;
    }
    if (is_already_used_item(child_idx, seq_length, parents)) {
      continue;
    } else {
      // printf("returning parent index: %i\n", parent_idx);
      return parent_idx;
    }    
  }

  return -1;
}

/**
   Finds min of two integers.
**/
int find_min(int a, int b) {
  return a < b ? a : b;
}

/**
   Finds maximum of provided int sequence.

   Returns: Index of the max element.
**/
int find_max(int *seq, int length) {
  int value = INT_MIN;
  int value_idx = -1;
  for (int i = 0; i < length; i++) {
    if (*(seq + i) > value) {
	value = *(seq + i);
	value_idx = i;
    }
  }

  return value;
}
  
int find_seq_length(Pair input_data[], int input_length) {
  IntTable *lengths = int_table_new(input_length + 1, input_length);
  IntTable *capacities = int_table_new(input_length + 1, input_length);
  IntTable *parents = int_table_new(input_length + 1, input_length);
  int_table_fill(parents, -1);
  
  for (int l = 0; l <= input_length; l++) {
    //printf("considering sequence of %i elements:\n", l);
    for (int t = 0; t < input_length; t++) {
      //printf("\tconsidering sequence ending on element %i:\n", t);
      int w = input_data[t].weight;
      int s = input_data[t].strength;
      if (l == 0) {
	int_table_set(parents, l, t, -1);
	continue;
      } else if (l == 1) {
	int_table_set(lengths, l, t, 1);
	int_table_set(parents, l, t, -1);
	int_table_set(capacities, l, t, s - w);
	continue;
      }

      int_table_set(parents, l, t, find_parent(l, t, capacities, parents));
      /* printf("\t\tparent element for (%i; %i): %i\n", l, t, */
      /* 	     int_table_get(parents, l, t)); */
      if (int_table_get(parents, l, t) == -1) {
	int_table_set(lengths, l, t, int_table_get(lengths, l - 1, t));
	int_table_set(parents, l, t, -1);
	int_table_set(capacities, l, t, 0);
	continue;
      }
      int parent_capacity = int_table_get(capacities, l - 1,
					  int_table_get(parents, l, t));
      int capacity = find_min(s, parent_capacity);
      if (capacity - w > 0) {
	int_table_set(capacities, l, t, capacity - w);
	int_table_set(lengths, l, t, l);
      } else {
	int_table_set(capacities, l, t, 0);
	int_table_set(lengths, l, t, int_table_get(lengths, l-1, t));
	int_table_set(parents, l, t, -1);
      }
    }
  }

  printf("Lengths table:\n");
  int_table_print(lengths);
  printf("Parents table:\n");
  int_table_print(parents);
  printf("Capacities table:\n");
  int_table_print(capacities);
  
  int seq_length = find_max(int_table_row(lengths, lengths->nrows - 1),
			    lengths->ncolumns);
  
  int_table_free(lengths);
  int_table_free(capacities);
  int_table_free(parents);
  return seq_length;
}
  
int main(int argc, char* argv[]) {
  union {
    char a[10];
    int i;
  } a_union;
  int *pint = (int*)&a_union;
  *pint = 5;
  
  Pair input[5607] = {};
  int data = 0, i = 0, input_length = 0;
  
  while (scanf("%i", &data) != EOF) {
    if (i % 2 == 0) {
      input[input_length].weight = data;
    } else {
      input[input_length].strength = data;
    }

    i += 1;
    if (i > 1) {
      i = 0;
      input_length += 1;
    }
  }

  
  printf("read %i input entities:\n", input_length);
  for (int i = 0; i < input_length; i++) {
    printf("\tinput %i (weight; strength): %i; %i\n",
	   i, input[i].weight, input[i].strength);
  }
  int seq_length = find_seq_length(input, input_length);
  printf("longest sequence: %i\n", seq_length);  
}
