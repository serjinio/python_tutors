
#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>


/**
   A cutting task data structure
**/
typedef struct {
  int length;
  int *cuts;
  int num_cuts;
} cutting_task;


cutting_task *cutting_task_new(int total_length, int num_cuts, int *cuts) {
  cutting_task *task = malloc(sizeof(cutting_task));
  if (task == NULL) {
    return NULL;
  }
  
  task->length = total_length;
  task->num_cuts = num_cuts;
  task->cuts = malloc(sizeof(int) * num_cuts);
  memcpy(task->cuts, cuts, sizeof(int) * num_cuts);
  return task;
}


int cutting_task_free(cutting_task *task) {
  if (task == NULL) {
    return 0;
  }
  
  free(task->cuts);
  free(task);
  return 0;
}


int cutting_tasks_free(cutting_task *task[], int tasks_number) {
  int rt;
  
  for (int i = 0; i < tasks_number; i++) {
    rt = cutting_task_free(task[i]);
  }
  
  return 0;
}


void cutting_task_print(cutting_task *task) {
  if (task == NULL) {
    return;
  }

  printf("Cutting task:\n");
  printf("\t Total Length: %i\n", task->length);
  printf("\t Number of cuts: %i\n", task->num_cuts);
  printf("\t Cuts: ");
  for (int i = 0; i < task->num_cuts; i++) {
    printf("%i, ", task->cuts[i]);
  }
  printf("\n");
}


typedef struct {
  cutting_task *tasks[1000];
  int tasks_number;
} task_list;


task_list *task_list_new() {
  task_list *list = malloc(sizeof(task_list));
  if (list == NULL) {
    return NULL;
  }

  list->tasks_number = 0;
  memset(list->tasks, 0, sizeof(cutting_task *) * 1000);
  return list;
}


void task_list_free(task_list *list) {
  free(list);
}


int check_input_args(char const *input_filename) {
  if (strcmp(input_filename, "") == 0) {
    puts("Cannot accept empty string as an input filename!");
    return 1;
  }
  if (access(input_filename, F_OK) != 0) {
    puts("The filename specified does not exists!");
    return 1;
  }

  return 0;
}


task_list *read_input(char *filename) {
  task_list *cutting_tasks = task_list_new();
  int retcode = 0;
  FILE *fp;
  char *line = NULL;
  size_t len = 0;
  ssize_t read;

  fp = fopen(filename, "r");
  if (fp == NULL) {
    retcode = -1;
    goto finalize;
  }

  int length, num_cuts;
  int line_count = 0;
  int tasks_count = 0;
  while ((read = getline(&line, &len, fp)) != -1) {

    if (line_count % 3 == 0) { // reading total length
      length = atoi(line);
      if (length == 0) { // end of input
	retcode = 0;
	goto finalize;
      } 
    } else if (line_count % 3 == 1) { // reading cuts number
      num_cuts = atoi(line);
    } else if (line_count % 3 == 2) { // reading cuts placement
      int cut;
      int cuts[50];
      int cuts_found = 0;
      char *token = strtok(line, " ");
      while (token != NULL) {	
	cuts[cuts_found] = atoi(token);
	cuts_found += 1;
	token = strtok(NULL, " ");
      }
      
      cutting_task *task = cutting_task_new(length, num_cuts, cuts);
      printf("Read task #%i:\n", cutting_tasks->tasks_number);
      cutting_task_print(task);
      
      cutting_tasks->tasks[cutting_tasks->tasks_number] = task;
      cutting_tasks->tasks_number += 1;
    }
    
    line_count += 1;
  }

 finalize:
  if (fp) {
    fclose(fp);
  }
  if (line) {
    free(line);
  }

  if (retcode == 0) {
    return cutting_tasks;
  } else {
    task_list_free(cutting_tasks);
    return NULL;
  }
}


int compute_task_cost(cutting_task *task) {
  int memo[task->num_cuts][task->num_cuts];
  int parents[task->num_cuts][task->num_cuts];

  for (int i = 0; i < task->num_cuts; i++) {
    for (int k = 0; k < task->num_cuts; k++) {
      memo[i][k] = -1;
      parents[i][k] = -1;
    }
  }

  for (int i = 0; i < task->num_cuts; i++) {
    for (int k = 0; k < task->num_cuts; k++) {
      //int prev_cost = i == 0 ? INT_MAX : min(memo[i - 1]);
      
    }
  }
    
  return 0;
}


int compute_costs(task_list *tasks) {
  if (tasks == NULL) {
    return -1;
  }
  
  printf("Cutting costs:\n");
  for (int i = 0; i < tasks->tasks_number; i++) {
    int cost = compute_task_cost(tasks->tasks[i]);
    if (cost == -1) {
      printf("Program was unable to resolve task #%i!\n", i);
      return -1;
    }
    
    printf("Cost for task #%i: %i\n", i, cost);
  }

  return 0;
}


int main(int argc, char **argv) {
  int rc;
  
  if (argc != 2) {
    puts("This command should be provdied one input argument: "
	 "filename with input data. Exiting!");
    return 1;
  }

  char *input_filename = argv[1];
  if (check_input_args(input_filename) != 0) {
    puts("Inputs are not valid, the program will exit.");
    return 1;
  }

  printf("Reading input file: \"%s\"...\n", input_filename);
  task_list *cutting_tasks = read_input(input_filename);
  if (cutting_tasks == NULL) {
    puts("Failed to read input.");
    return 1;
  }

  printf("Read %i input tasks to resolve.\n", cutting_tasks->tasks_number);
  rc = compute_costs(cutting_tasks);
  if (rc != 0) {
    printf("Program failed to resolve one of the tasks, "
	   "due to some unexpected problem.\n");
  }

  cutting_tasks_free(cutting_tasks->tasks, cutting_tasks->tasks_number);
  
  return 0;
}
