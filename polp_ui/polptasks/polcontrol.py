############################################################
# tasks for control of hardware for polarization
############################################################


from invoke import task, run


@task
def sample():
    run("echo hello")
