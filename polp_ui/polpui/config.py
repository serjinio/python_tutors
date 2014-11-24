############################################################
# Configuration values for the app
############################################################

# Storage of acquired NMR signals
NMR_DATA_DIR = '/mnt/hgfs/lab_data/2013/0919'
NMR_DATA_DIR_APPEND_DATE_SUFFIX = False

NMR_FILENAME_PREFIX = 'nmr-'
NMR_FILENAME_SUFFIX = '.dat'

# MW/NMR mode control programs
MW_ON_EXEC = '/home/polp/GPIB/src/mwoff'
MW_OFF_EXEC = '/home/polp/GPIB/mwon'

# NMR acquisition programs

# creates .saveise in the current directory
DO_NMR_EXEC = '/home/polp/GPIB/nmr'
