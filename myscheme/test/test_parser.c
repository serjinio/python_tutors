/*
  Tests for hash container
*/

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <assert.h>

#include "ast.h"
#include "parser.h"

#include <check.h>


START_TEST(test_lexer_basic)
{
  char *instr;
  asprintf(&instr, "( (sample (string)) )");
  sa_list *token_list = tokenize(instr);
  ck_assert(sa_list_length(token_list) == 8);
}
END_TEST

START_TEST(test_parser_basic)
{
  char *instr;
  asprintf(&instr, "( sample ( string 5 more ) ) ");
  sa_list *token_list = tokenize(instr);
  ms_ast *ast = parse(token_list);

  char *repr = ast_to_repr(ast);
  printf("AST repr: '%s'\n", repr);
  
  ck_assert(strcmp(repr, instr) == 0);
  
  free(repr);
}
END_TEST

START_TEST(test_parser_specforms)
{
  char *instr;
  asprintf(&instr, "( + 5 5 ) ");
  sa_list *token_list = tokenize(instr);
  ms_ast *ast = parse(token_list);
  
  char *repr = ast_to_repr(ast);
  printf("AST repr: '%s'\n", repr);
  
  ck_assert(strcmp(repr, instr) == 0);
  
  free(repr);
}
END_TEST

START_TEST(test_parser_nil)
{
  char *instr;
  asprintf(&instr, "( nil ) ");
  sa_list *token_list = tokenize(instr);
  ms_ast *ast = parse(token_list);
  
  char *repr = ast_to_repr(ast);
  printf("AST repr: '%s'\n", repr);
  
  ck_assert(strcmp(repr, instr) == 0);
  
  free(repr);
}
END_TEST

START_TEST(test_interp_basic)
{
  char *instr;
  asprintf(&instr, "(print (+ 5 5)) (print (+ 6 6))");
  ms_ast *root = parse(tokenize(instr));
  eval_program(root);
}
END_TEST


Suite *parser_suite(void)
{
  Suite *s;
  TCase *tc_basic;

  s = suite_create("Parser");

  tc_basic = tcase_create("Basic");

  tcase_add_test(tc_basic, test_lexer_basic);
  tcase_add_test(tc_basic, test_parser_basic);
  tcase_add_test(tc_basic, test_parser_specforms);
  tcase_add_test(tc_basic, test_parser_nil);
  suite_add_tcase(s, tc_basic);
  
  return s;
}

Suite *interp_suite(void)
{
  Suite *s;
  TCase *tc_basic;

  s = suite_create("Interpreter");

  tc_basic = tcase_create("Basic");

  tcase_add_test(tc_basic, test_interp_basic);
  suite_add_tcase(s, tc_basic);

  return s;
}

int run_suite(Suite *suite) {
  int number_failed;
  SRunner *sr_suite = srunner_create(suite);
  
  srunner_run_all(sr_suite, CK_NORMAL);
  number_failed = srunner_ntests_failed(sr_suite);
  srunner_free(sr_suite);
  
  return number_failed;
}

int main(void)
{
  int number_failed = 0;
  Suite *parser, *interp;

  parser = parser_suite();
  number_failed += run_suite(parser);

  interp = interp_suite();
  number_failed += run_suite(interp);

  return (number_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
