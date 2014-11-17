############################################################
# tasks for NMR acquisition
############################################################


from invoke import task, run


@task
def sample():
    run("echo hello")
