import dupchecker as DC
import makemaster as MM
import split as SPL
import info as INF
import corruptfiles as CF

SOURCE_FOLDERS = [
    "/media/PiTB/foofuck/Clean",
    "/media/PiTB/foofuck/test2",
    "/media/PiTB/foofuck/test3",
]
DESTINATION_BASE_FOLDER = "/home/whitepi/MasterPicsDeduped"
MAX_FOLDER_SIZE_GB = 1.85

infototals = []
for folder in SOURCE_FOLDERS:
    print(f"\nProcessing folder: {folder}")
    infmain = INF.ExtCount(folder).get_ext_count()
    infototals = infototals.append(infmain)
infototals = sum(infototals)
print(f"\nTotal Count from all folders: {infototals}")

corrupted_total = []
for cor_file in SOURCE_FOLDERS:
    print(f"\nChecking for corrupted files in folder: {cor_file}")
    corruptfiles = CF(cor_file).corruptfiles_main()
    corrupted_total = corrupted_total.append(corruptfiles)
corrupted_total = sum(corrupted_total)
print(f"\nTotal corrupted files found and deleted from all folders: {corrupted_total}")

for dup in SOURCE_FOLDERS:
    print(f"\nChecking for duplicates in folder: {dup}")
    dcmain = DC.dupchecker_main(dup)
    print(f"\nFinished checking for duplicates in folder: {dup}")



# splmain = SPL.split_main(SOURCE_FOLDER, DESTINATION_BASE_FOLDER, MAX_FOLDER_SIZE_GB)
