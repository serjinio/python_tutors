/**
   Interpreter implementation
**/

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <stdarg.h>
#include <assert.h>

#include "env.h" 
#include "interp.h"


// forward declarations

static ms_obj *prim_plus(sa_list *params, ms_env *env);
static ms_obj *prim_print(sa_list *params, ms_env *env);


// private helpers

/**
   convenience structure for proc calls info
**/
typedef struct proc_call_info {
  char *proc_name;
  sa_list_node *proc_args;
} proc_call_info;


static void
error(char *format, ...) {
  char msgbuf[512];
  va_list args;
  va_start(args, format);
  vsnprintf(msgbuf, 512, format, args);
  va_end(args);
  
  printf("%s: %s\n", "ERROR", msgbuf);
  exit(1);
}

// a global environment
static ms_env *global_env;

// vars to hold references to global constants
static ms_obj *nil = NULL;
static ms_obj *t = NULL;

static ms_env *
make_global_env() {
  ms_env *env = env_new(NULL);
  char *s_name = NULL;
  ms_obj *rt_obj = NULL;
  
  nil = obj_mknil();
  asprintf(&s_name, "%s", "nil");
  env_put(env, s_name, nil);

  t = obj_mkbool();
  asprintf(&s_name, "%s", "t");
  env_put(env, s_name, t);

  asprintf(&s_name, "%s", "+");
  rt_obj = obj_mkprimop(prim_plus);
  env_put(env, s_name, rt_obj);

  asprintf(&s_name, "%s", "print");
  rt_obj = obj_mkprimop(prim_print);
  env_put(env, s_name, rt_obj);
  
  return env;
}

// value constructors

/**
   constructor for nil runtime object. should be the only nil in
   interpreter runtime.
**/
ms_obj *
obj_mknil() {
  ms_obj *obj = malloc(sizeof(ms_obj));

  *obj = (ms_obj){.type = T_NIL};
  
  return obj;
}

ms_obj *
obj_mkbool() {
  ms_obj *obj = malloc(sizeof(ms_obj));

  *obj = (ms_obj){.type = T_BOOL};
  
  return obj;
}

ms_obj *
obj_mkint(int int_value) {
  ms_obj *obj = malloc(sizeof(ms_obj));

  *obj = (ms_obj){.type = T_INT, .int_value = int_value};
  printf("made T_INT with value: %i\n", int_value);
  return obj;
}

ms_obj *
obj_mkfloat(float float_value) {
  ms_obj *obj = malloc(sizeof(ms_obj));
 
  *obj = (ms_obj){.type = T_FLOAT, .float_value = float_value};
  
  return obj;
}

ms_obj *
obj_mkproc(ms_ast *proc_ast) {
  ms_obj *obj = malloc(sizeof(ms_obj));

  *obj = (ms_obj){.type = T_PROC, .proc_ast = proc_ast};
  
  return obj;
}

ms_obj *
obj_mkprimop(primop_fn impl_fn) {
  ms_obj *obj = malloc(sizeof(ms_obj));

  *obj = (ms_obj){.type = T_PRIMOP, .primop_impl_fn = impl_fn};
  
  return obj;
}

void obj_free(ms_obj *obj) {
  assert(obj != NULL);
  
  free(obj);
}

// evals for atoms

ms_obj *
eval_symbol(ms_ast *ast, ms_env *env) {
  assert(ast != NULL && env != NULL);
  printf("resolving reference to symbol: %s\n", ast->symbol_name);
  
  ms_obj *obj = env_get(env, ast->symbol_name);
  if (obj == NULL) {
    error("reference to unbound symbol: %s", ast->symbol_name);
  }
  
  return obj;
}

// function call

#define is_callable(obj) ((obj)->type == T_PROC || (obj)->type == T_PRIMOP)

static char *
get_proc_name(ms_ast *ast) {
  assert(ast != NULL);
  
  if (ast->list == NULL) {
    error("This is not a callable expression");
  }

  if (sa_list_length(ast->list) < 1) {
    error("Invalid input list");
  }

  char *proc_name = NULL;
  sa_list_node *lst_head = sa_list_head(ast->list);
  ms_ast *ast_proc_name = (ms_ast *)sa_list_value(lst_head);
  
  if (ast_proc_name->kind != AST_SYMBOL) {
    error("invalid list format for procedure call - first item must be proc name");
  }

  proc_name = ast_proc_name->symbol_name;
  assert(proc_name != NULL);
  return proc_name;
}

static sa_list *
eval_primop_args(ms_ast *proc_ast, ms_env *env) {
  assert(proc_ast != NULL && env != NULL);
  
  if (proc_ast->list == NULL) {
    error("This is not callable expression");
  }

  if (sa_list_length(proc_ast->list) < 1) {
    error("Invalid list for proc call: should have at least 1 item");
  }

  sa_list *params_lst = sa_list_new(NULL);
  sa_list_node *args_lst_node = sa_list_next(sa_list_head(proc_ast->list));
  while (args_lst_node != NULL) {
    ms_ast *ast_arg = (ms_ast *)sa_list_value(args_lst_node);
    ms_obj *proc_param = eval(ast_arg, env);
    sa_list_append(params_lst, proc_param);
    
    args_lst_node = sa_list_next(args_lst_node);
  }

  return params_lst;
}

static ms_obj *
eval_proc_call(ms_ast *ast, ms_env *env) {
  assert(ast != NULL && env != NULL);

  ms_obj *ret_val = NULL;

  char *proc_name = get_proc_name(ast);
  ms_obj *proc_obj = env_get(env, proc_name);
  if (proc_obj == NULL) {
    error("cannot find proc with given name: %s", proc_name);
  }
  
  if (!is_callable(proc_obj)) {
    error("given symbol is not of a callable type");
  }

  if (proc_obj->type == T_PRIMOP) {
    sa_list *params = eval_primop_args(ast, env);
    ret_val = proc_obj->primop_impl_fn(params, env);
    sa_list_free(params);
  } else {
    error("user defined procs not implemented yet");
    ret_val = NULL;
  }

  // we should not return C NULLs at all
  assert(ret_val != NULL);
  return ret_val;
}

// primitive procs

#define is_number(n) ((n)->type == T_INT || (n)->type == T_FLOAT)


static ms_obj *
prim_plus(sa_list *params, ms_env *env) {
  assert(params != NULL);

  if (sa_list_length(params) != 2) {
    error("+ operator requires 2 parameters");
  }
  
  sa_list_node *lst_node = sa_list_head(params);
  ms_obj *op_a = (ms_obj *)sa_list_value(lst_node);
  lst_node = sa_list_next(lst_node);
  ms_obj *op_b = (ms_obj *)sa_list_value(lst_node);

  if (!is_number(op_a) || !is_number(op_b)) {
    error("+ operator requires numeric data types only");
  }
    
  if (op_a->type == T_FLOAT && op_b->type == T_FLOAT) {
    return obj_mkfloat(op_a->float_value + op_b->float_value);
  } else if (op_a->type == T_INT && op_b->type == T_INT) {
    return obj_mkint(op_a->int_value + op_b->int_value);
  }

  // should not reach
  error("operands passsed to '+' operator have incompatible types");
  return NULL;
}

static ms_obj *
prim_print(sa_list *params, ms_env *env) {
  assert(params != NULL);
  
  if (sa_list_length(params) != 1) {
    error("print operator requires exactly 1 argument");
  }

  sa_list_node *lst_node = sa_list_head(params);
  assert(lst_node != NULL);
  ms_obj *argument = (ms_obj*)sa_list_value(lst_node);
  assert(argument != NULL);

  switch (argument->type) {
  case T_NIL:
    printf("%s\n", "nil");
    break;
  case T_BOOL:
    printf("%s\n", "t");
    break;
  case T_INT:
    printf("%i\n", argument->int_value);
    break;
  case T_FLOAT:
    printf("%f\n", argument->float_value);
    break;
  case T_PROC:
    printf("<lambda>\n");
    break;
  case T_PRIMOP:
    printf("<primop>\n");
    break;
  }

  return nil;
}

// main dispatch proc

ms_obj *
eval(ms_ast *ast, ms_env *env) {
  assert(ast != NULL);

  printf("in eval(), current AST node: "); ast_print_node_kind(ast); printf("\n");
  /* printf("env dump follows:\n"); */
  /* env_dump(env); */
  /* printf("env dump finish\n"); */
  
  switch (ast->kind) {
  case AST_ROOT:
    {
      sa_list *program_expr_lst = ast->expr_list;
      sa_list_node *expr_lst_node = sa_list_head(program_expr_lst);
      while (expr_lst_node != NULL) {
	ms_ast *expr_ast = (ms_ast *)(sa_list_value(expr_lst_node));
	eval(expr_ast, env);

	expr_lst_node = sa_list_next(expr_lst_node);
      }
    }
    break;
  case AST_NIL:
    return nil;
    break;
  case AST_INT:
    return obj_mkint(ast->int_value);
    break;
  case AST_FLOAT:
    return obj_mkfloat(ast->float_value);
    break;
  case AST_SYMBOL:
    return eval_symbol(ast, env);
    break;
  case AST_PRIMOP_PLUS:
  case AST_PRIMOP_MINUS:
  case AST_PRIMOP_MULT:
  case AST_PRIMOP_DIV:
  case AST_PRIMOP_PRINT:
  case AST_LIST:
    return eval_proc_call(ast, env);
    break;
  case AST_SPFORM_IF:
  case AST_SPFORM_DEFINE:
  case AST_SPFORM_QUOTE:
  case AST_SPFORM_LAMBDA:
  case AST_SPFORM_SET:
    error("this special form is not implemented");
    break;
  }
  
  return nil;
}

int
eval_program(ms_ast *ast) {
  assert(ast != NULL);

  if (ast->kind != AST_ROOT) {
    error("Invalid node type given for top-level node, execution aborted");
  }

  global_env = make_global_env();
  if (global_env == NULL) {
    error("Failed to initialize global environment");
  }
  
  eval(ast, global_env);
  
  return 0;
}
