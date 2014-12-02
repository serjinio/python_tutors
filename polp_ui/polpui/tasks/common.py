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
        err = TaskError(
            'Subprocess: "{}" thrown an error.'.format(command), e)
        logging.error(err)
        raise err


def _check_cmd_return_code(command, return_code, stdout, stderr):
    if return_code == 0:
        return
    err = TaskError(
        ('Subprocess: "{}" returned non-zero '
         'return code: {}. \nSubprocess stdout:\n{}\n'
         'Subproces stderr:\n{}').format(
             str(command), return_code, stdout, stderr))
    logging.error(err)
    raise err


class TaskError(Exception):
    """Error which is thrown if task execution went wrong."""

    def __init__(self, msg, inner=None):
        super(TaskError, self).__init__(msg, inner)
        self.msg = msg
        self.inner = inner
