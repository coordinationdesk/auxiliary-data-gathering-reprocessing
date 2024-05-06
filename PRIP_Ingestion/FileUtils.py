import re
import os

#Resolve a path with env var
def fully_resolve(a_path, check_existence=False):
    resolved = os.path.expanduser(os.path.expandvars(a_path))
    if "$" in resolved:
        raise Exception("Environment variable not resolved in %s" % resolved)
    if check_existence:
        if not os.path.exists(resolved):
            raise Exception("File not found %s" % resolved)
    return resolved


#merge the input folder in the given one by puting symbolic links to files
def folder_fusion(an_input_dir, a_dest_dir):
    try:
        os.mkdir(a_dest_dir)
    except OSError as e:
        if not os.path.exists(a_dest_dir):
            raise
    #list the alternative files
    for strRoot, listDirNames, listFileNames in os.walk(an_input_dir):
        # for all dirs underneath
        for strDirName in listDirNames:
            strAlternativeDir = os.path.join(strRoot, strDirName)
            strLinkDir = a_dest_dir + os.sep + strAlternativeDir.replace(an_input_dir, "",1)
            if not os.path.exists(strLinkDir):
                try:
                    os.mkdir(strLinkDir)
                except OSError as e:
                    if not os.path.exists(strLinkDir):
                        raise
        # for all files underneath
        for strFileName in listFileNames:
            strAlternativeFile = os.path.join(strRoot, strFileName)
            strLinkFile = a_dest_dir + os.sep + strAlternativeFile.replace(an_input_dir, "",1)
            strRelAlternativeFile = os.path.relpath(strAlternativeFile, os.path.dirname(strLinkFile))
            if not os.path.exists(strLinkFile):
                try:
                    os.symlink(strRelAlternativeFile, strLinkFile)
                except OSError as e:
                    if not os.path.exists(strLinkFile):
                        raise Exception("Internal error with file: "+strLinkFile)
    
def save_tuples_to_file(lta_files, output_file):
    print("Files: ", lta_files)
    output_names_file = f"{output_file}.status"
    with open(output_names_file, "w+") as onf:
        aux_writer = csv.writer(onf)
        for au_rec in lta_files:
            aux_writer.writerow(au_rec)

def save_list_to_file(lta_files, output_file):
    print("Files: ", lta_files)
    # removesuffix only from 3.9
    lta_names_list = [file[1][:-4] if file[1].endswith('.TGZ') else file[1]
                      for file in lta_files]
    print("Filenames: ", lta_names_list)
    # Reorder fields in lta_files
    # removesuffix only from 3.9
    lta_status_files = [(rec[1][:-4] if rec[1].endswith('.TGZ') else rec[1], *rec[2:4], rec[0])
                      for rec in lta_files]
    output_names_file = f"{output_file}.names"
    with open(output_names_file, "w+") as onf:
        for name in lta_names_list:
            onf.write(name)
            onf.write('\n')


