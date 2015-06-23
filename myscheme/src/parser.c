/**
   Frontend - lexer & parser, creates AST from input source string
**/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include <assert.h>

#include "parser.h"


// private helpers

#define token_node_value(sa_lst_node) ((char *)sa_list_value((sa_lst_node)))


static int g_parser_error = PARSER_E_OK;

int
get_parser_error() {
  return g_parser_error;
}


static const char* SIMPLE_TOKENS = "()";


static _Bool is_simple_token(char token) {
  for (const char *ch = SIMPLE_TOKENS; *ch != '\0'; ch++) {
    if (token == *ch) {
      return true;
    } 
  }
  return false;
}
  
static char *copy_char_bytes(const char *str, int num_chars) {
  char *copy = malloc(sizeof(char) * (num_chars + 1));
  memcpy(copy, str, num_chars);
  copy[num_chars] = '\0';
  return copy;
}

static int get_next_token_length(const char *start) {
  assert(start != NULL);
  if (*start == '\0') {
    return 0;
  }
  // if we have simple token return it
  if (is_simple_token(*start)) {
    return 1;
  }
  
  const char *ch = start + 1;
  int token_len = 1;
  
  while (*ch != '\0') {
    if (isspace(*ch)) {
      break;
    }
    if (is_simple_token(*ch)) {
      break;
    }
    
    ch += 1;
    token_len += 1;
  }
  
  return token_len;
}


// lexer public interface


sa_list *
tokenize(char *input_str) {
  sa_list *lst = sa_list_new(NULL);

  const char *s = input_str;
  int token_len = get_next_token_length(s);
  
  while (token_len != 0) {
    char *token_copy = copy_char_bytes(s, token_len);
    // printf("DEBUG: found token: %s\n", token_copy);    
    sa_list_append(lst, token_copy);
    
    s += token_len;
    while (isspace(*s)) s++;
    token_len = get_next_token_length(s);
  }
   
  return lst;
}


// parser private helpers

static void
set_parser_error(int err_code) {
  g_parser_error = err_code;
}

_Bool
str_equals(char *str, char *compare_str) {
  assert(str != NULL && compare_str != NULL);
  
  if (strcmp(str, compare_str) == 0) {
    return true;
  } else {
    return false;
  }
}

#define token_equals(token, compare_str) str_equals((token), (compare_str))

int is_str_numeric(const char *s)
{
    if (s == NULL || *s == '\0' || isspace(*s))
      return 0;
    char * p;
    strtod (s, &p);
    return *p == '\0';
}

static ms_ast *
parse_number(sa_list_node **token_node) {
  char *token_value = token_node_value(*token_node);
  assert(is_str_numeric(token_value) == true);
  
  int int_value = atoi(token_value);
  ms_ast *ast_node = ast_int_new(int_value);
  *token_node = sa_list_next(*token_node);
  
  return ast_node;
}

static ms_ast *
parse_atomic_token(sa_list_node **token_node) {
  char *token_value = token_node_value(*token_node);
  
  if (is_str_numeric(token_value) == true) {
    return parse_number(token_node);
  } else {
    ms_ast *symbol_token = ast_symbol_new(token_value);
    *token_node = sa_list_next(*token_node);
    return symbol_token;
  }
}

/**
   Returns type of the given list. By default AST node type for a list
   is a generic AST_LIST, which should become a proc call expression.
   This function detects if first element of the list signals
   that it is one of special forms and returns type of this special
   form, or just a generic AST_LIST otherwise.
**/
static ms_ast_node_kind
get_list_type(sa_list *lst) {
  assert(sa_list_length(lst) >= 1);

  ms_ast *head_item = (ms_ast *)sa_list_value(sa_list_head(lst));
    
  switch (head_item->kind) {
  case AST_SYMBOL:
    {
      char *s_name = head_item->symbol_name;
      if (str_equals(s_name, "if")) {
	return AST_SPFORM_IF;
      } else if (str_equals(s_name, "define")) {
	return AST_SPFORM_DEFINE;
      } else if (str_equals(s_name, "quote")) {
	return AST_SPFORM_QUOTE;
      } else if (str_equals(s_name, "lambda")) {
	return AST_SPFORM_LAMBDA;
      } else if (str_equals(s_name, "set")) {
	return AST_SPFORM_SET;
      } else if (str_equals(s_name, "print")) {
	return AST_PRIMOP_PRINT;
      } else if (str_equals(s_name, "+")) {
	return AST_PRIMOP_PLUS;
      } else if (str_equals(s_name, "-")) {
	return AST_PRIMOP_MINUS;
      } else if (str_equals(s_name, "/")) {
	return AST_PRIMOP_DIV;
      } else if (str_equals(s_name, "*")) {
	return AST_PRIMOP_MULT;
      } else {
	return AST_LIST;
      }
      break;
    }
  default:
    // by default all lists are given generic AST_LIST type
    return AST_LIST;
  }
}

static ms_ast *
parse_list(sa_list_node **token_node) {
  // list should begin with "(" token
  // make this check, and if it does, advance to list' first item
  if (!token_equals(token_node_value(*token_node), "(")) {
    set_parser_error(PARSER_E_INVALID_SYNTAX);
    return NULL;
  } else {
    *token_node = sa_list_next(*token_node);
  }

  sa_list *lst = sa_list_new(NULL);
  ms_ast *ast_node = ast_list_new(lst);
  
  while (*token_node != NULL) {
    char *token_value = token_node_value(*token_node);
    // printf("DEBUG: parsing on token: %s\n", token_value);
    
    if (token_equals(token_value, ")")) { // list end
      ast_node->kind = get_list_type(lst);    
      *token_node = sa_list_next(*token_node);
      goto finish_ok;
    } else if (token_equals(token_value, "(")) { // new list start
      ms_ast *list_ast_node = parse_list(token_node);
      
      if (list_ast_node == NULL) {
	goto list_parse_error;
      } else {
	printf("appending list node\n");
      	sa_list_append(lst, list_ast_node);
      }
    } else {
      ms_ast *atom_ast_node = parse_atomic_token(token_node);
      sa_list_append(lst, atom_ast_node);
    }
  }

 finish_ok:
  return ast_node;
  
 list_parse_error:
  sa_list_free(lst);
  ast_free(ast_node);
  ast_node = NULL;
  return NULL;
}


// parser public interface

ms_ast *
parse(sa_list *tokens) {
  sa_list_node *token_node = sa_list_head(tokens);
  ms_ast *ast_root = ast_root_new();

  while(token_node != NULL) {
    ms_ast *list_ast_node = parse_list(&token_node);
    sa_list_append(ast_root->expr_list, list_ast_node);
  }

  return ast_root;
}

