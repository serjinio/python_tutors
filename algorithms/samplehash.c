/**
   Sample of a hash store
**/

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <assert.h>

#define HASH_BINS_NO 100


/************************************************************
 Sample hash function
************************************************************/

unsigned long
hash_string(unsigned char *str)
{
  unsigned long hash = 5381;
  int c;

  while (c = *str++)
    hash = ((hash << 5) + hash) + c; /* hash * 33 + c */

  return hash % HASH_BINS_NO;
}


/************************************************************
 Data structures & their functions
************************************************************/

struct sm_hash_item {
  void *value;
  struct sm_hash_item *next;
};

struct sm_hash_items_list {
  struct sm_hash_item *head;
  int size;
};

/* sm_hash - a sample hash declaration */
struct sm_hash {
  struct sm_hash_items_list *store_lists;
  int bins_no;
};

struct sm_hash *
sm_hash_new() {
  struct sm_hash *hash = malloc(sizeof(struct sm_hash));
  hash->bins_no = HASH_BINS_NO;

  hash->store_lists = malloc(sizeof(struct sm_hash_items_list) * hash->bins_no);
  for (int i = 0; i < hash->bins_no; i++) {
    struct sm_hash_items_list *plst = hash->store_lists + i;
    plst->head = NULL;
    plst->size = 0;
}
  
return hash;
}

_Bool
sm_hash_contains(struct sm_hash *hash, char *value) {
  int value_hash = hash_string(value);
  assert(value_hash < HASH_BINS_NO);
  struct sm_hash_items_list *lst = hash->store_lists + value_hash;
  struct sm_hash_item *item = lst->head;
  
  while (item != NULL) {
    char *item_value = (char *)item->value;
    if (strcmp(item_value, value) == 0) {
      return true;
    }
    item = item->next;
  }

  return false;
}

int
sm_hash_add(struct sm_hash *hash, char *value) {
  if (sm_hash_contains(hash, value)) {
    return -2;
  }

  // construct new value
  struct sm_hash_item *item = malloc(sizeof(struct sm_hash_item));
  if (item == NULL) {
    return -1;
  }
  item->value = value;
  
  // put it into hash
  int value_hash = hash_string(value);
  assert(value_hash < HASH_BINS_NO);
  struct sm_hash_items_list *lst = hash->store_lists + value_hash;
  if (lst->head == NULL) {
    lst->head = item;
  } else {
    item->next = lst->head;
    lst->head = item;
  }
  lst->size += 1;
  
  return 0;
}

int
sm_hash_count(struct sm_hash *hash) {
  int count = 0;
  for (int i = 0; i < hash->bins_no; i++) {
    struct sm_hash_items_list *lst = hash->store_lists + i;
    count += lst->size;
  }
  return count;
}

void
sm_hash_items_list_print(struct sm_hash_items_list *lst) {
  struct sm_hash_item *item = lst->head;
  while (item != NULL) {
    printf("  '%s'\n", (char *)item->value);
    item = item->next;
  }
}

void
sm_hash_print(struct sm_hash *hash) {
  printf("printing hash contents. hash bins no.: %d\n", hash->bins_no);
  for (int i = 0; i < hash->bins_no; i++) {
    printf("contents of bin no.: %d\n:", i);
    struct sm_hash_items_list *lst = hash->store_lists + i;
    sm_hash_items_list_print(lst);
  }
}

void
sm_hash_print_bin_lengths(struct sm_hash *hash) {
  for (int i = 0; i < hash->bins_no; i++) {
    struct sm_hash_items_list *lst = hash->store_lists + i;
    printf("bin # %d length: %d\n", i, lst->size);
  }
}


static char *rand_str(char *str, size_t length) {
  static int seed = 3457;
  const char const *charset =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-#'?!";

  if (str == NULL)
    return NULL;
      
  srand(time(NULL) * length + seed);
  seed += 2;
  length--;
  for (int i = 0; i < length; i++) {
    int key = rand() % (int)(sizeof(charset) - 1);
    str[i] = charset[key];
  }
  str[length] = '\0';
  
  // printf("generated random string: %s\n", str);
  return str;
}


static inline char *
rand_str_alloc(size_t length) {
  return length ? rand_str(malloc(sizeof(char) * length), length) : NULL;
}


void
basic_test() {
  struct sm_hash *hash = sm_hash_new();
  char *val;
  
  printf("test add one...\n");
  asprintf(&val, "%s", "sample value one");
  sm_hash_add(hash, val);
  assert(sm_hash_count(hash) == 1);
  assert(sm_hash_contains(hash, val) == true);
  assert(sm_hash_contains(hash, "bad value") == false);
  printf("passed.\n");
  printf("hash after one addition:\n");
  sm_hash_print(hash);
  
  printf("test add 99 items...\n");
  for (int i = 0; i < 99; i++) {
    val = rand_str_alloc(9);
    sm_hash_add(hash, val);
  }
  //sm_hash_print_bin_lengths(hash);
  assert(sm_hash_count(hash) == 100);
  printf("passed.\n");
}


void
perf_test() {
  printf("performance tests...\n");
  struct sm_hash *hash = sm_hash_new();

  char *val;

  printf("test add many items...\n");
  for (int i = 0; i < 10000; i++) {
    val = rand_str_alloc(10);
    sm_hash_add(hash, val);
  }
  //sm_hash_print_bin_lengths(hash);
  //assert(sm_hash_count(hash) == 10000);
  printf("passed.\n");

}
  
  
int main() {
  printf("sample hash type. performing tests...\n");
  
  //basic_test();

  perf_test();
  
  printf("finished\n");
}
