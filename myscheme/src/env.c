/**
   Implementation of a dictionary for symbol tracking
**/

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <assert.h>

#include "interp.h"
#include "env.h"


// private helpers

static unsigned int
hash_symbol_name(sa_hmap_key key) {
  unsigned char *str = (unsigned char *)key;
  unsigned int hash = 5381;
  int c;

  while ((c = *str++)) {
    hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
  }

  return hash;
}

static _Bool
symbol_names_equal(sa_hmap_key key1, sa_hmap_key key2) {
  char *s1 = (char *)key1;
  char *s2 = (char *)key2;

  if (strcmp(s1, s2) == 0) {
    return true;
  } else {
    return false;
  }
}

static void
keyval_free(sa_hmap_keyval *keyval) {
  assert(keyval != NULL);
  
  obj_free((ms_obj *)keyval->value);
  free((char *)keyval->key);
  sa_hmap_keyval_free(keyval);
}

// public interface

ms_env *
env_new(ms_env *parent_env) {
  ms_env *env = malloc(sizeof(ms_env));
  if (env == NULL) {
    return NULL;
  }

  sa_hmap *symbols_map = sa_hmap_new(hash_symbol_name,
				     symbol_names_equal);
  if (symbols_map == NULL) {
    free(env);
    return NULL;
  }

  *env = (ms_env){.parent = parent_env, .symbols = symbols_map};
  
  return env;
}

void env_free(ms_env *env) {
  // TODO: with proper symbols cleanup
}

int
env_put(ms_env *env, char *symbol_name, ms_obj *obj) {
  if (sa_hmap_contains(env->symbols, (sa_hmap_key)symbol_name)) {
    sa_hmap_keyval *keyval =
      sa_hmap_remove(env->symbols, (sa_hmap_key)symbol_name);
    keyval_free(keyval);
  }

  char *s_name;
  asprintf(&s_name, "%s", symbol_name);
  sa_hmap_add(env->symbols, s_name, obj);
  return 0;
}

ms_obj *
env_get(ms_env *env, char *symbol_name) {
  if (!sa_hmap_contains(env->symbols, symbol_name)) {
    return NULL;
  }

  return sa_hmap_get(env->symbols, symbol_name);
}

void
env_dump(ms_env *env) {
  assert(env != NULL);
  
  sa_hmap_iter *iter = sa_hmap_iter_new(env->symbols);
  sa_hmap_keyval *keyval;
  
  while ( (keyval = sa_hmap_iter_next(iter)) != NULL ) {
    char *key = (char*)keyval->key;
    ms_obj *value = (ms_obj *)keyval->value;

    assert(value != NULL);
    switch (value->type) {
    case T_NIL:
      printf("%s (%s): %s\n", key, "nil", "nil");
      break;
    case T_BOOL:
      printf("%s (%s): %s\n", key, "bool", "t");
      break;
    case T_INT:
      printf("%s (%s): %i\n", key, "integer", value->int_value);
      break;
    case T_FLOAT:
      printf("%s (%s): %f\n", key, "integer", value->float_value);
      break;
    case T_PROC:
      printf("%s (%s): %p\n", key, "lambda", value->proc_ast);
      break;
    case T_PRIMOP:
      printf("%s (%s): %p\n", key, "primop", value->primop_impl_fn);
      break;
    }
  }

  
}
