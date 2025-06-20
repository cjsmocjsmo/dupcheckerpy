import dupchecker as DC
import makemaster as MM
import split as SPL
import info as INF

SOURCE_FOLDER = "/home/whitepi/MasterPics"
DESTINATION_BASE_FOLDER = "/home/whitepi/MasterPicsDeduped"
MAX_FOLDER_SIZE_GB = 1.85


dcmain = DC.dupchecker_main(SOURCE_FOLDER)
mmmain = MM.main(SOURCE_FOLDER)
splmain = SPL.split_main(SOURCE_FOLDER, DESTINATION_BASE_FOLDER, MAX_FOLDER_SIZE_GB)
infmain = INF.ExtCount(SOURCE_FOLDER).get_ext_count()