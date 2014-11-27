"""
Routines common to all tasks.
"""

import os
import logging
import subprocess


def execute(command, cwd=os.getcwd()):
    _check_cmd_return_code(command, *_execute_cmd(command, cwd=cwd))
        

def _execute_cmd(command, cwd=os.getcwd()):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, cwd=cwd)
        out, err = process.communicate()
        return (process.returncode, out, err)
    except Exception as e:
        logging.warn('During execution of: "{}" an error occurred: "{}"'
                     .format(command, e))
        raise TaskError(
            'Subprocess: "{}" thrown an error.'.format(command), e)
    

def _check_cmd_return_code(command, return_code, stdout, stderr):
    if return_code == 0:
        return
    logging.warn(('Execution of: "{}" returned non-zero '
                  'return code: "{}". \nSubprocess stdout:\n{}\n'
                  'Subproces stderr:\n{}').format(
                      command, return_code, stdout, stderr))
    raise TaskError(
        ('Subprocess: "{}" returned non-zero '
         'return code: {}. \nSubprocess stdout:\n{}\n'
         'Subproces stderr:\n{}').format(
             str(command), return_code,
             stdout, stderr))

    
class TaskError(Exception):
    """Error which is  thrown if task execution went wrong."""
    
    def __init__(self, msg, inner=None):
        super(TaskError, self).__init__(msg, inner)
        self.msg = msg
        self.inner = inner
