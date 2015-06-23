/**
   Interface of the parser
**/

#ifndef MYSC_PARSER_H
#define MYSC_PARSER_H

#include <simpalg/list.h>

#include "ast.h"

/**
   Makes a list of tokens out of input string
**/
sa_list *tokenize(char *input_str);

/**
   Constructs AST out of token list
**/
ms_ast *parse(sa_list *tokens);


// error reporting

typedef enum {
  PARSER_E_OK,
  PARSER_E_INVALID_SYNTAX,
  PARSER_E_INVALID_STATE
} ms_parser_error;

/**
   In case of parse error, returns error code or PARSER_E_OK if all is ok.
**/
int get_parser_error();


#endif
