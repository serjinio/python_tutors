

from fabric.api import task, run, env
from fabric.operations import put
import os
import logging


env.user = 'root'
env.dotfiles_dir = '../../dotfiles'
env.screenrc_config = os.path.join(env.dotfiles_dir, 'screenrc')
env.emacs_config = os.path.join(env.dotfiles_dir, 'emacs')


logging.basicConfig(level=logging.WARN,
                    format='%(levelname)s:  %(message)s')


############################################################
# Tasks
############################################################


@task(default=True)
def setup():
    setup_mosh()
    setup_screen()
    setup_emacs()
    

############################################################
# Helpers
############################################################


def setup_mosh():
    run('yum install mosh')


def setup_screen():
    if env.get('screenrc_config') and \
       os.path.exists(env.screenrc_config):
        put(env.screenrc_config, '~/.screenrc')
    else:
        logging.warn(('Cannot setup screen on target host, config file "{}"'
                      'missing on local host!').format(env.screenrc_config))


def setup_emacs():
    if env.get('emacs_config') and \
       os.path.exists(env.emacs_config):
        put(env.emacs_config, '~/.emacs')
    else:
        logging.warn(('Cannot setup emacs on target host, config file "{}"'
                      'missing on local host!').format(env.emacs_config))

