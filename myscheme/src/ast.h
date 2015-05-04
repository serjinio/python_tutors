/**
   AST
**/


#ifndef MYSC_AST_H
#define MYSC_AST_H

#include <simpalg/list.h>


typedef enum {
  // Root node - global level
  AST_ROOT,
  // Atoms
  AST_NIL, AST_INT, AST_FLOAT, AST_SYMBOL,
  // Special forms
  AST_SPFORM_IF, AST_SPFORM_DEFINE, AST_SPFORM_QUOTE,
  AST_SPFORM_LAMBDA, AST_SPFORM_SET,
  // Primitive operators
  AST_PRIMOP_PLUS, AST_PRIMOP_MINUS, AST_PRIMOP_MULT,
  AST_PRIMOP_DIV, AST_PRIMOP_PRINT,
  // Basic composite data structure
  AST_LIST
} ms_ast_node_kind;

enum ms_ast_walk_direction { 
  AST_WALK_UP, AST_WALK_DOWN
};

typedef struct ms_ast {
  ms_ast_node_kind kind;
  union {
    sa_list *expr_list; // for root node
    int int_value;
    float float_value;
    char *symbol_name;
    sa_list *list;
  };
} ms_ast;


// helper functions to create AST nodes

ms_ast *ast_root_new();
ms_ast *ast_int_new(int int_value);
ms_ast *ast_float_new(float float_value);
ms_ast *ast_symbol_new(char *symbol_name);
ms_ast *ast_symbol_if_new(sa_list *test_form,
			  sa_list *conseq_form, sa_list *alt_form);

ms_ast *ast_list_new(sa_list *list);
void ast_free(ms_ast *ast_node);

/**
   Signature for tree visitor function.

   Params:
     user_data: Optional parameter to store useful user info
       during tree traversal.
**/
typedef void (*ast_visitor_fn)(ms_ast *ast, enum ms_ast_walk_direction,
			       void *user_data);

/**
   Walks the given tree
**/
void ast_walk(ms_ast *ast, ast_visitor_fn fn,
	      void *user_data);

/**
   Prints AST to stdout
**/
void ast_print_str(ms_ast *ast);

/**
   Prints source representation to stdout
**/
char *ast_ro_repr(ms_ast *ast);

/**
   Prints node kind
**/
void ast_print_node_kind(ms_ast *ast_node);


#endif
