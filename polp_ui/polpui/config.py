############################################################
# Configuration values for the app
############################################################

# Storage of acquired NMR signals
NMR_DATA_DIR = '/home/polp/data/2014/'
NMR_DATA_DIR_APPEND_DATE_SUFFIX = True

NMR_FILENAME_PREFIX = 'nmr-'
NMR_FILENAME_SUFFIX = '.dat'

# MW/NMR mode control programs
MW_ON_EXEC = '/home/polp/GPIB/src/mwon'
MW_OFF_EXEC = '/home/polp/GPIB/src/mwoff'

# NMR acquisition programs

# creates .saveise in the current directory
DO_NMR_EXEC = '/home/polp/GPIB/src/nmr'
NMR_DATA_FILE_NAME = 'ise0.dat'
