/*
  cdecl - parser for C type declarations - it translates
    type declarations into readable english phrase.
    At the moment only partially implemented - declaration
    parsing logic is in place, but types qualifiers recognition
    is nowhere complete.
*/
    
#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <stdbool.h>
#include <assert.h>


#define _TESTING


/************************************************************
 Data structures & their functions
************************************************************/

struct token_list_node {
  struct token_list_node *next;
  char *token;
};

static struct token_list_node *token_list_node_new(char *token) {
  struct token_list_node *node = malloc(sizeof(struct token_list_node));
  node->next = NULL;
  asprintf(&(node->token), "%s", token);
  return node;
}

int token_list_node_free(struct token_list_node *node) {
  assert(node != NULL);
  free(node->token);
  free(node);
}

struct tokens_list {
  struct token_list_node *head;
  struct token_list_node *tail;
  int length;
};

static struct tokens_list *tokens_list_new() {
  struct tokens_list *lst = malloc(sizeof(struct tokens_list));
  lst->head = NULL;
  lst->tail = NULL;
  lst->length = 0;
  return lst;
}

static void tokens_list_free(struct tokens_list *list) {
  assert(list != NULL);
  struct token_list_node *node = list->head;
  
  while (node != NULL) {
    struct token_list_node *prev_node = node;
    node = node->next;
    token_list_node_free(prev_node);
  }

  free(list);
}

static void tokens_list_push(struct token_list_node *node,
			     struct tokens_list *list) {
  assert(list != NULL);
  struct token_list_node *head = list->head;
  
  if (head == NULL) {
    list->tail = node;
  } else {
    node->next = head;
  }
  list->head = node;
  list->length += 1;
}

static struct token_list_node *tokens_list_pop(struct tokens_list *list) {
  assert(list != NULL);
  if (list->length == 0) {
    return NULL;
  }
  
  struct token_list_node *head = list->head;
  struct token_list_node *second = list->head->next;
  if (list->length == 1) {
    list->head = NULL;
    list->tail = NULL;
  } else {
    list->head = second;
  }

  list->length -= 1;
  return head;
}

static struct tokens_list *tokens_list_reverse(struct tokens_list *list) {
  assert(list != NULL);
  struct tokens_list *rev_list = tokens_list_new();
  struct token_list_node *node = list->head;

  struct token_list_node *rev_list_next_node = NULL;
  while (node != NULL) {
    struct token_list_node *rev_list_node = token_list_node_new(node->token);
    if (node == list->head) {
      rev_list->tail = rev_list_node;
    }
    if (node == list->tail) {
      rev_list->head = rev_list_node;
    }
    if (rev_list_next_node != NULL) {
      rev_list_node->next = rev_list_next_node;
    }
    node = node->next;
    rev_list_next_node = rev_list_node;
  }

  rev_list->length = list->length;
  return rev_list;    
}

static struct tokens_list *
tokens_list_split_on_node(struct tokens_list *list,
			  struct token_list_node *node) {
  struct token_list_node *list_node = list->head;
  struct token_list_node *prev_list_node = NULL;
  int node_index = 0;
  
  while (list_node != NULL) {
    if (list_node == node) {
      break;
    }
    
    prev_list_node = list_node;
    list_node = list_node->next;
    node_index += 1;
  }

  if (list_node == NULL) {
    return NULL;
  }
  
  struct tokens_list *split_list = tokens_list_new();
  split_list->head = list_node;
  split_list->tail = list->tail;
  split_list->length = list->length - node_index;

  list->length = list->length - split_list->length;
  if (prev_list_node != NULL) {
    prev_list_node->next = NULL;
    list->tail = prev_list_node;
  }
  if (list_node == list->head) {
    list->head = NULL;
    list->tail = NULL;
  }

  return split_list;
}

static void tokens_list_print(struct tokens_list *list) {
  assert(list != NULL);

  if (list->length == 0) {
    printf("this tokens list is empty.\n");
    return;
  }

  printf("tokens list:\n");
  struct token_list_node *node = list->head;
  while (node != NULL) {
    printf("\t'%s'\n", node->token);
    node = node->next;
  } 
}

/************************************************************
 Scanner
************************************************************/


const char* SIMPLE_TOKENS = "()[]*";


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

struct tokens_list *tokenize(const char *input_string) {
  assert(input_string != NULL);
  printf("tokenizing input: '%s'\n", input_string);
  
  struct tokens_list *tokens_list = tokens_list_new();
  const char *s = input_string;
  int token_len = get_next_token_length(s);
  
  while (token_len != 0) {
    char *token_copy = copy_char_bytes(s, token_len);
    struct token_list_node *node = token_list_node_new(token_copy);
    tokens_list_push(node, tokens_list);
    free(token_copy);
    
    s += token_len;
    while (isspace(*s)) s++;
    token_len = get_next_token_length(s);
  }

  struct tokens_list *rev_tokens_list = tokens_list_reverse(tokens_list);
  tokens_list_free(tokens_list);
  
  return rev_tokens_list;
}

/************************************************************
 Parser
************************************************************/


const char *TYPE_NAMES[] = {"int", "char", "float", "double", "\0"};
const char *TYPE_QUALIFIERS[] = {"const", "static", "volatile", "*", "\0"};
  

static _Bool is_type_name(char *token) {
  int idx = 0;
  const char *type_name = TYPE_NAMES[idx];  

  while (type_name[0] != '\0') {
    if (strcmp(token, type_name) == 0) {
      return true;
    }
    
    idx += 1;
    type_name = TYPE_NAMES[idx];
  }
  
  return false;
}

static _Bool is_type_qualifier(char *token) {
  int idx = 0;
  const char *type_qualifier = TYPE_QUALIFIERS[idx];  

  while (type_qualifier[0] != '\0') {
    if (strcmp(token, type_qualifier) == 0) {
      return true;
    }
    
    idx += 1;
    type_qualifier = TYPE_QUALIFIERS[idx];
  }
  
  return false;
}

static _Bool is_identifier(char *token) {
  for (char *ch = token; *ch != '\0'; ch++) {
    if (!isalnum(*ch)) {
      return false;
    }
  }
  if (is_type_name(token) || is_type_qualifier(token)) {
    return false;
  }
  
  return true;
}

static _Bool is_digits_only(char *str) {
  for (char *ch = str; *ch != '\0'; ch++) {
    if (!isdigit(*ch)) {
      return false;
    }
  }
  return true;
}

static struct token_list_node *find_identifier_node(struct tokens_list *list) {
  assert(list != NULL);
  struct token_list_node *node = list->head;

  while (node != NULL) {
    if (is_identifier(node->token)) {
      return node;
    }
    node = node->next;
  }

  return NULL;
}

static struct token_list_node *
get_next_decl_token(struct tokens_list *left,
		    struct tokens_list *right,
		    int *direction) {
  assert(left != NULL && right != NULL);
  if (left->length == 0 && right->length == 0) {
    return NULL;
  }

  struct token_list_node *node = NULL;
  if (*direction > 0) {
    if (right->length > 0) {
      node = tokens_list_pop(right);
    } else {
      node = tokens_list_pop(left);
    }
  } else {
    if (left->length > 0) {
      node = tokens_list_pop(left);
    } else {
      node = tokens_list_pop(right);
    }
  }

  assert(node != NULL);
  
  if (*direction > 0) {
    if (strcmp(node->token, ")") == 0) {
      *direction *= -1;
    }
  } else {
    if (strcmp(node->token, "(") == 0) {
      *direction *= -1;
    }
  } 
	       
  return node;
}

static char *translate_token(char *token, int parse_direction) {
  assert(token != NULL);
  
  char *str = NULL;
  
  if (strcmp(token, "int") == 0) {
    asprintf(&str, "%s", "integer");
  } else if (strcmp(token, "*") == 0) {
    asprintf(&str, "%s", "pointer-to");
  } else if (strcmp(token, "const") == 0) {
    asprintf(&str, "%s", "read-only");
  } else if (strcmp(token, "[") == 0) {
    asprintf(&str, "%s", "array of");
  } else if (strcmp(token, "]") == 0) {
    asprintf(&str, "%s", "");
  } else if (strcmp(token, "(") == 0 && parse_direction > 0) {
    asprintf(&str, "%s", "function, returning");
  } else if (is_digits_only(token)) {
    asprintf(&str, "%s %s", token, "elements of");
  } else {
    asprintf(&str, "%s", token);
  }

  return str;
}

int suppress_redundant_decl_tokens(const char *current_token,
				   const int direction,
				   struct tokens_list *left_part,
				   struct tokens_list *right_part) {
  if (direction > 0) {
    // if that's a function ptr declaration, then just skip until
    // its arguments list closes      
    if (strcmp(current_token, "(") == 0) {
      struct token_list_node *token_node = NULL;
      _Bool finished = false;
      while(!finished) {
	token_node = tokens_list_pop(right_part);
	if (token_node != NULL) {
	  if (strcmp(token_node->token, ")") == 0) finished = true;
	  token_list_node_free(token_node);
	}
      }
    }
  }

  return 0;
}

_Bool should_translate(const char *token, int parse_direction) {
  if (parse_direction < 0) {
    if (strcmp(token, "(") == 0) {
      return false;
    }
  } else {
    if (strcmp(token, ")") == 0) {
      return false;
    }
  }
  
  return true;
}

static char *translate_tokens(struct tokens_list *list) {
  printf("starting tokens translation...\n");

  _Bool witherr = false;
  
  struct token_list_node *name_node = find_identifier_node(list);
  if (name_node == NULL) {
    printf("Syntax Error: unable to find identifier in the supplied declaration!\n");
    return NULL;
  }

  struct tokens_list *right_part = tokens_list_split_on_node(list, name_node);
  struct tokens_list *left_part = tokens_list_reverse(list);
  name_node = tokens_list_pop(right_part);
  
  int direction = +1;
  char *translation = NULL;
  asprintf(&translation, "%s%s%s", "declare ", name_node->token, " as ");
  token_list_node_free(name_node);
  
  while(left_part->length > 0 || right_part->length > 0) {
    int token_direction = direction;
    struct token_list_node *token_node =			
      get_next_decl_token(left_part, right_part, &direction);
    assert(token_node != NULL);
    
    if (should_translate(token_node->token, token_direction)) {
      char *token_translation = translate_token(token_node->token,
						token_direction);
      char *prev_translation = translation;
      asprintf(&translation, "%s%s%s", prev_translation,
	     token_translation, " ");      
      free(token_translation);
      free(prev_translation);
    }
    int rt = 0;
    rt = suppress_redundant_decl_tokens(token_node->token,
					token_direction,
					left_part, right_part);
    
    token_list_node_free(token_node);
    if (rt != 0) {
      printf("Syntax Error: malformed declaration!\n");
      witherr = true;
      goto exit;
    }
  }

 exit:
  tokens_list_free(right_part);
  tokens_list_free(left_part);
  
  if (!witherr) {
    return translation;
  } else {
    return NULL;
  }
}

static char *translate_decl(char *decl) {
  printf("starting translation...\n");

  struct tokens_list *tokens_list = tokenize(decl);
  char *translation = translate_tokens(tokens_list);
  tokens_list_free(tokens_list);
  printf("translated tokens:\n\t%s\n", translation);
  
  printf("execution finished.\n");
  return translation;
}

/************************************************************
 Testing
************************************************************/

static void test_scanner() {
  printf("executing scanner test cases\n");
  struct tokens_list * tokens;

  tokens = tokenize("const int *var");
  assert(tokens->length == 4);
  tokens_list_free(tokens);
  
  tokens = tokenize("const int *var[100]");
  assert(tokens->length == 7);
  tokens_list_free(tokens);

  tokens = tokenize("char * (*fn)(void)");
  assert(tokens->length == 9);
  tokens_list_free(tokens);
  
  printf("scanner test finished\n");
}

static void test_parser() {
  printf("executing parser test cases\n");
  char *translated_decl;

  translated_decl = translate_decl("const int (*var)[100]");
  free(translated_decl);

  translated_decl = translate_decl("int *(*fn)(void)[100]");
  free(translated_decl);
  
  printf("parser test cases finished\n");
}

static void run_tests() {
  printf("starting execution of cdecl test suite...\n");
  test_scanner();
  test_parser();
  printf("test suite execution finished.\n");
}

/************************************************************
 Main
************************************************************/

void main(int argc, char* argv[]) {
#ifdef _TESTING
  run_tests();
#else
  
  if (argc < 2) {
    printf("ERROR: this program requires at "
	   "least one command line argument\n");
    printf("ERROR: - a declaration to parse!\n");
    return;
  }
  
  char *input_decl = argv[1];
  char *translation = translate_decl(input_decl);

  printf("translated declaration:\n\t%s\n", translation);
  free(translation);
  
#endif
}
