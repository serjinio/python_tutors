############################################################
# main file for polp task definition
############################################################


from invoke import Collection
from tasks import nmr, polcontrol


ns = Collection(nmr, polcontrol)

