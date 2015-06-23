/**
   Implementation of supporting functions for AST
**/

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <assert.h>

#include <simpalg/list.h>

#include "ast.h"


ms_ast *
ast_root_new() {
  ms_ast *ast = malloc(sizeof(ms_ast));
  if (ast == NULL) {
    return NULL;
  }
  
  sa_list *lst = sa_list_new(NULL);
  
  *ast = (ms_ast){.kind = AST_ROOT, .expr_list = lst};
  
  return ast;
}

ms_ast *
ast_int_new(int int_value) {
  ms_ast *ast = malloc(sizeof(ms_ast));
  if (ast == NULL) {
    return NULL;
  }

  *ast = (ms_ast){.kind = AST_INT, .int_value = int_value};

  return ast;
}

ms_ast *
ast_float_new(float float_value) {
  ms_ast *ast = malloc(sizeof(ms_ast));
  if (ast == NULL) {
    return NULL;
  }

  *ast = (ms_ast){.kind = AST_FLOAT, .float_value = float_value};

  return ast;
}

ms_ast *
ast_symbol_new(char *symbol_name) {
  ms_ast *ast = malloc(sizeof(ms_ast));
  if (ast == NULL) {
    return NULL;
  }

  char *ast_symbol_name;
  asprintf(&ast_symbol_name, "%s", symbol_name);
  *ast = (ms_ast){.kind = AST_SYMBOL, .symbol_name = ast_symbol_name};

  return ast;
}

ms_ast *
ast_list_new(sa_list *list) {
  ms_ast *ast = malloc(sizeof(ms_ast));
  if (ast == NULL) {
    return NULL;
  }

  *ast = (ms_ast){.kind = AST_LIST, .list = list};

  return ast;
}

static void
ast_print_str_fn(ms_ast *ast, enum ms_ast_walk_direction dir,
		 void *user_data) {
  assert(ast != NULL);

  if (dir != AST_WALK_DOWN) {
    return;
  }
  
  switch (ast->kind) {
  case AST_ROOT:
    printf("AST root node!\n");
    break;
  case AST_LIST:
    printf("list...\n");
    break;
  case AST_SYMBOL:
    printf("symbol: %s\n", ast->symbol_name);
    break;
  case AST_NIL:
    printf("nil\n");
    break;
  case AST_INT:
    printf("int constant: %i\n", ast->int_value);
    break;
  case AST_FLOAT:
    printf("float constant: %f\n", ast->float_value);
    break;
  case AST_SPFORM_IF:
  case AST_SPFORM_DEFINE:
  case AST_SPFORM_QUOTE:
  case AST_SPFORM_LAMBDA:
  case AST_SPFORM_SET:
    {
      sa_list_node *lst_head = sa_list_head(ast->list);
      char *sf_name = ((ms_ast *)sa_list_value(lst_head))->symbol_name;
      printf("special form: '%s'...\n", sf_name);
      break;
    }
  case AST_PRIMOP_PLUS:
  case AST_PRIMOP_MINUS:
  case AST_PRIMOP_MULT:
  case AST_PRIMOP_DIV:
  case AST_PRIMOP_PRINT:
    {
      sa_list_node *lst_head = sa_list_head(ast->list);
      char *op_name = ((ms_ast *)sa_list_value(lst_head))->symbol_name;
      printf("primitive operator: '%s'...\n", op_name);
      break;
    }
  }
}

static void
ast_print_repr_fn(ms_ast *ast, enum ms_ast_walk_direction dir,
		  void *mem_buf) {
  assert(ast != NULL);

  char *str_buf = (char *)mem_buf;
  char tmp_str_buf[256];
  
  switch (ast->kind) {
  case AST_ROOT:
    // no op
    break;
  case AST_LIST:
  case AST_SPFORM_IF:
  case AST_SPFORM_DEFINE:
  case AST_SPFORM_QUOTE:
  case AST_SPFORM_LAMBDA:
  case AST_SPFORM_SET:
  case AST_PRIMOP_PLUS:
  case AST_PRIMOP_MINUS:
  case AST_PRIMOP_MULT:
  case AST_PRIMOP_DIV:
  case AST_PRIMOP_PRINT:
    if (dir == AST_WALK_DOWN) {
      strcat(str_buf, "( ");
    } else {
      strcat(str_buf, ") ");
    }
    break;
  case AST_SYMBOL:
    strcat(str_buf, ast->symbol_name);
    strcat(str_buf, " ");
    break;
  case AST_NIL:
    strcat(str_buf, "nil");
    break;
  case AST_INT:
    sprintf(tmp_str_buf, "%i", ast->int_value);
    strcat(str_buf, tmp_str_buf);
    strcat(str_buf, " ");
    break;
  case AST_FLOAT:
    sprintf(tmp_str_buf, "%f", ast->float_value);
    strcat(str_buf, tmp_str_buf);
    strcat(str_buf, " ");
    break;
  }
}

void
ast_print_str(ms_ast *ast) {
  assert(ast != NULL);
  ast_walk(ast, ast_print_str_fn, NULL);
}

char *
ast_to_repr(ms_ast *ast) {
  assert(ast != NULL);

  char *repr = malloc(sizeof(char) * 1024);
  memset(repr, 0, sizeof(char) * 1024);
  ast_walk(ast, ast_print_repr_fn, repr);
  
  return repr;
}

void
ast_walk(ms_ast *ast, ast_visitor_fn fn,
		  void *user_data) {
  assert(ast != NULL);
  
  sa_list_node *lst_node;
    
  switch (ast->kind) {
  case AST_ROOT:
  case AST_SPFORM_IF:
  case AST_SPFORM_DEFINE:
  case AST_SPFORM_QUOTE:
  case AST_SPFORM_LAMBDA:
  case AST_SPFORM_SET: 
  case AST_PRIMOP_PLUS:
  case AST_PRIMOP_MINUS:
  case AST_PRIMOP_MULT:
  case AST_PRIMOP_DIV:
  case AST_PRIMOP_PRINT:
  case AST_LIST:
    
    fn(ast, AST_WALK_DOWN, user_data);
    
    if (ast->kind == AST_ROOT) {
      lst_node = sa_list_head(ast->expr_list);
    } else {
      lst_node = sa_list_head(ast->list);
    }
    
    while(lst_node != NULL) {
      ms_ast *child = sa_list_value(lst_node);
      ast_walk(child, fn, user_data);
      
      lst_node = sa_list_next(lst_node);
    }

    fn(ast, AST_WALK_UP, user_data);
    
    break;
  default:
    fn(ast, AST_WALK_DOWN, user_data);
  }
}

static void ast_root_free(ms_ast *ast_root) {
  assert(ast_root != NULL && ast_root->kind == AST_ROOT);
  
  sa_list_free(ast_root->expr_list);
  free(ast_root);
}

static void ast_nil_free(ms_ast *ast_node) {
  assert(ast_node != NULL && ast_node->kind == AST_NIL);

  free(ast_node);
}

static void ast_number_free(ms_ast *ast_number) {
  assert(ast_number != NULL &&
	 (ast_number->kind == AST_INT || ast_number->kind == AST_FLOAT));
  
  free(ast_number);
}

static void ast_symbol_free(ms_ast *ast_symbol) {
  assert(ast_symbol != NULL && ast_symbol->kind == AST_SYMBOL);

  free(ast_symbol->symbol_name);
  free(ast_symbol);
}

static void ast_list_free(ms_ast *ast_list) {
  assert(ast_list != NULL && ast_list->kind == AST_LIST);

  sa_list_free(ast_list->list);
  free(ast_list);
}

void
ast_free(ms_ast *ast_node) {
  
  switch (ast_node->kind) {
  case AST_ROOT:
    ast_root_free(ast_node);
    break;
  case AST_NIL:
    ast_nil_free(ast_node);
    break;
  case AST_INT:
    ast_number_free(ast_node);
    break;
  case AST_FLOAT:
    ast_number_free(ast_node);
    break;
  case AST_SYMBOL:
    ast_symbol_free(ast_node);
    break;
  case AST_SPFORM_IF:
  case AST_SPFORM_DEFINE:
  case AST_SPFORM_QUOTE:
  case AST_SPFORM_LAMBDA:
  case AST_SPFORM_SET: 
  case AST_PRIMOP_PLUS:
  case AST_PRIMOP_MINUS:
  case AST_PRIMOP_MULT:
  case AST_PRIMOP_DIV:
  case AST_PRIMOP_PRINT:
  case AST_LIST:
    ast_list_free(ast_node);
    break;
  }
  
}

void
ast_print_node_kind(ms_ast *ast_node) {

  switch (ast_node->kind) {
  case AST_ROOT:
    printf("%s", "AST_ROOT");
    break;
  case AST_NIL:
    printf("%s", "AST_NIL");
    break;
  case AST_INT:
    printf("%s", "AST_INT");
    break;
  case AST_FLOAT:
    printf("%s", "AST_FLOAT");
    break;
  case AST_SYMBOL:
    printf("%s", "AST_SYMBOL");
    break;
  case AST_SPFORM_IF:
    printf("%s", "AST_SPFORM_IF");
    break;
  case AST_SPFORM_DEFINE:
    printf("%s", "AST_SPFORM_DEFINE");
    break;
  case AST_SPFORM_QUOTE:
    printf("%s", "AST_SPFORM_QUOTE");
    break;
  case AST_SPFORM_LAMBDA:
    printf("%s", "AST_SPFORM_LAMBDA");
    break;
  case AST_SPFORM_SET:
    printf("%s", "AST_SPFORM_SET");
    break;
  case AST_PRIMOP_PLUS:
    printf("%s", "AST_PRIMOP_PLUS");
    break;
  case AST_PRIMOP_MINUS:
    printf("%s", "AST_PRIMOP_MINUS");
    break;
  case AST_PRIMOP_MULT:
    printf("%s", "AST_PRIMOP_MULT");
    break;
  case AST_PRIMOP_DIV:
    printf("%s", "AST_PRIMOP_DIV");
    break;
  case AST_PRIMOP_PRINT:
    printf("%s", "AST_PRIMOP_PRINT");
    break;
  case AST_LIST:
    printf("%s", "AST_LIST");
    break;
  }

}
