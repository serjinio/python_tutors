/**
   Definition of environment object for symbol management
**/


#ifndef MYSC_ENV_H
#define MYSC_ENV_H

#include <simpalg/hmap.h>


// Forward decls
typedef struct ms_obj ms_obj;

/**
   Structure to hold program symbols
   parent pointer - provides access to parent env for symbol
     resolution in multi-scope scenarios. Currently only one
     global env is used.
**/
typedef struct ms_env {
  struct ms_env *parent;
  sa_hmap *symbols;
} ms_env;

/**
   Convenience structure to store symbol name and its
   associated runtime value together.
**/
typedef struct ms_symval {
  char *name;
  ms_obj *value;
} ms_symval;

ms_env *env_new(ms_env *parent_env);
void env_free(ms_env *env);

/**
   Adds new symbol to the env. In case symbol with a
   given name already exists it will be returned.
**/
int env_put(ms_env *env, char *symbol_name, ms_obj *obj);

/**
   Gets a symbol from the env.
**/
ms_obj *env_get(ms_env *env, char *symbol_name);

/**
   Dumps the contents of environment to stdout
**/
void env_dump(ms_env *env);

#endif 
