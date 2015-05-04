/**
   Defines all runtime structures and algorithms necessary to process
   AST constructed by parser.
**/


#ifndef MYSC_INTERP_H
#define MYSC_INTERP_H

#include "ast.h"


// Forward declarations
typedef struct ms_obj ms_obj;
typedef struct ms_env ms_env;

/**
   Fundamental runtime datatypes
**/
enum ms_obj_type {
  T_NIL, T_BOOL, T_INT, T_FLOAT, T_PROC, T_PRIMOP
};

/**
   Implementation function signature for primitive operators
**/
typedef ms_obj *(*primop_fn)(sa_list *params, ms_env *env);

/**
   Basic memory structure
**/
typedef struct ms_obj {
  enum ms_obj_type type;
  union {
    int int_value;
    float float_value;
    ms_ast *proc_ast;
    primop_fn primop_impl_fn;
  };
} ms_obj;

ms_obj *obj_mknil();
ms_obj *obj_mkbool();
ms_obj *obj_mkint(int int_value);
ms_obj *obj_mkfloat(float float_value);
ms_obj *obj_mkproc(ms_ast *proc_ast);
ms_obj *obj_mkprimop(primop_fn impl_fn);
void obj_free(ms_obj *obj);


/**
   Executes given AST
**/
ms_obj *eval(ms_ast *ast, ms_env *env);

/**
   Convenience method - starts program execution.
   The argument should be of AST_ROOT node kind.
**/
int eval_program(ms_ast *ast);

/**
   Evaluates a symbol - returns any value bound to a given program entity.
**/
ms_obj *eval_symbol(ms_ast *ast, ms_env *env);

#endif
