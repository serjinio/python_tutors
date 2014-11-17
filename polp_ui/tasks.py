############################################################
# main file for polp task definition
############################################################


from invoke import Collection
from polptasks import nmr, polcontrol


ns = Collection(nmr, polcontrol)

